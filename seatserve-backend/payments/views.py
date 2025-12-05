"""
Payment views for Stripe integration
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import UserRateThrottle
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
import logging
import json
import stripe

from payments.models import Payment
from payments.serializers import (
    PaymentSerializer, PaymentDetailSerializer, CreateCheckoutSessionSerializer,
    ConfirmPaymentSerializer, RefundPaymentSerializer
)
from payments.stripe_service import StripePaymentService
from orders.models import Order
from restaurants.models import Restaurant
from restaurants.permissions import IsRestaurantUser

logger = logging.getLogger(__name__)
payment_logger = logging.getLogger('payment')
security_logger = logging.getLogger('security')


class WebhookThrottle(UserRateThrottle):
    """Rate limit webhook endpoints"""
    scope = 'webhook'


class PaymentViewSet(viewsets.ModelViewSet):
    """Payment management with Stripe integration"""
    serializer_class = PaymentSerializer
    permission_classes = (IsAuthenticated, IsRestaurantUser)

    def get_queryset(self):
        """Get payments for current user's restaurant"""
        restaurant = Restaurant.objects.filter(owner=self.request.user).first()
        if restaurant:
            return Payment.objects.filter(restaurant=restaurant).order_by('-created_at')
        return Payment.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PaymentDetailSerializer
        return PaymentSerializer

    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's payments"""
        from django.utils.timezone import now
        
        today = now().date()
        restaurant = Restaurant.objects.filter(owner=request.user).first()
        if not restaurant:
            return Response(
                {'detail': 'Restaurant not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        payments = Payment.objects.filter(
            restaurant=restaurant,
            created_at__date=today
        ).order_by('-created_at')
        
        serializer = PaymentSerializer(payments, many=True)
        
        # Calculate totals
        completed = sum(p.amount for p in payments if p.status == 'COMPLETED')
        pending = sum(p.amount for p in payments if p.status == 'PENDING')
        
        return Response({
            'payments': serializer.data,
            'summary': {
                'completed': float(completed),
                'pending': float(pending),
                'count': len(payments)
            }
        })

    @action(detail=False, methods=['post'])
    def create_checkout(self, request):
        """Create Stripe checkout session for an order"""
        serializer = CreateCheckoutSessionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        order_id = serializer.validated_data['order_id']
        
        try:
            order = Order.objects.get(id=order_id)
            restaurant = order.restaurant
            
            # Check permission
            if restaurant.owner != request.user:
                return Response(
                    {'detail': 'Not authorized'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Check if payment already exists
            if hasattr(order, 'payment') and order.payment.status == 'COMPLETED':
                return Response(
                    {'detail': 'Order already paid'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create checkout session
            session_data = StripePaymentService.create_checkout_session(order, request)
            
            # Create or update payment record
            payment, created = Payment.objects.get_or_create(
                order=order,
                defaults={
                    'restaurant': restaurant,
                    'amount': order.total,
                    'currency': 'USD',
                    'payment_method': 'STRIPE',
                }
            )
            
            payment.session_id = session_data['session_id']
            payment.status = 'PENDING'
            payment.ip_address = self._get_client_ip(request)
            payment.user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
            payment.save()
            
            logger.info(f"Checkout session created: {payment.id} - {session_data['session_id']}")
            
            return Response({
                'payment_id': payment.id,
                'session_id': session_data['session_id'],
                'client_secret': session_data.get('client_secret'),
                'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
            }, status=status.HTTP_201_CREATED)
            
        except Order.DoesNotExist:
            return Response(
                {'detail': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Checkout creation failed: {str(e)}")
            return Response(
                {'detail': f'Failed to create checkout: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'])
    def confirm_payment(self, request):
        """Confirm payment status from Stripe session"""
        serializer = ConfirmPaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        session_id = serializer.validated_data['session_id']
        
        try:
            # Get session from Stripe
            session_data = StripePaymentService.confirm_payment(session_id)
            
            # Find payment record
            payment = Payment.objects.get(session_id=session_id)
            
            # Check permission
            if payment.restaurant.owner != request.user:
                return Response(
                    {'detail': 'Not authorized'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Update payment status based on Stripe response
            if session_data['payment_status'] == 'paid':
                payment.status = 'COMPLETED'
                payment.gateway_reference = session_data['payment_intent']
                payment.save()
                
                # Update order status
                order = payment.order
                if order.status == 'PENDING':
                    order.status = 'RECEIVED'
                    order.save()
                
                logger.info(f"Payment confirmed: {payment.id}")
                
                return Response({
                    'status': 'success',
                    'payment': PaymentDetailSerializer(payment).data,
                    'order_id': order.id,
                }, status=status.HTTP_200_OK)
            
            elif session_data['payment_status'] == 'unpaid':
                return Response({
                    'status': 'unpaid',
                    'message': 'Payment not yet completed'
                }, status=status.HTTP_200_OK)
            
            else:
                return Response({
                    'status': 'unknown',
                    'message': 'Unknown payment status'
                }, status=status.HTTP_200_OK)
            
        except Payment.DoesNotExist:
            return Response(
                {'detail': 'Payment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Payment confirmation failed: {str(e)}")
            return Response(
                {'detail': f'Failed to confirm payment: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail='pk', methods=['post'])
    def refund(self, request, pk=None):
        """Refund a payment"""
        payment = self.get_object()
        
        # Check permission
        if payment.restaurant.owner != request.user:
            return Response(
                {'detail': 'Not authorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = RefundPaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        refund_amount = serializer.validated_data.get('amount')
        reason = serializer.validated_data.get('reason', 'Customer requested refund')
        
        try:
            if not payment.is_refundable:
                return Response(
                    {'detail': f'Payment cannot be refunded. Status: {payment.get_status_display()}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Process refund with Stripe
            if payment.payment_method == 'STRIPE' and payment.gateway_reference:
                refund_data = StripePaymentService.refund_payment(
                    payment.gateway_reference,
                    refund_amount
                )
                
                payment.status = 'REFUNDED'
                payment.refund_amount = refund_amount or payment.amount
                payment.refund_reason = reason
                payment.refund_gateway_reference = refund_data['id']
                from django.utils import timezone
                payment.refunded_at = timezone.now()
                payment.save()
                
                logger.info(f"Payment refunded: {payment.id} - Refund ID: {refund_data['id']}")
                
                return Response({
                    'status': 'refunded',
                    'payment': PaymentDetailSerializer(payment).data,
                    'refund_id': refund_data['id'],
                }, status=status.HTTP_200_OK)
            
            else:
                return Response(
                    {'detail': 'Only Stripe payments can be refunded'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
        except Exception as e:
            logger.error(f"Refund failed: {str(e)}")
            return Response(
                {'detail': f'Failed to process refund: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def _get_client_ip(request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookViewSet(viewsets.ViewSet):
    """Handle Stripe webhooks with secure signature verification"""
    throttle_classes = [WebhookThrottle]
    permission_classes = (AllowAny,)

    @action(detail=False, methods=['post'])
    def webhook(self, request):
        """
        ✅ SECURE: Handle Stripe webhook events with signature verification
        
        Stripe sends events to this endpoint when:
        - Payment succeeded
        - Payment failed
        - Refund completed
        - Dispute opened
        """
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
        
        if not endpoint_secret:
            security_logger.error('STRIPE_WEBHOOK_SECRET not configured')
            return Response(
                {'error': 'Webhook not configured'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        try:
            # ✅ VERIFY SIGNATURE FIRST before processing
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
            security_logger.info(f'Webhook signature verified: {event["id"]}')
        except ValueError as e:
            security_logger.error(f'Invalid webhook payload: {str(e)}')
            return Response(
                {'error': 'Invalid payload'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except stripe.error.SignatureVerificationError as e:
            security_logger.warning(f'Webhook signature verification failed: {str(e)}')
            return Response(
                {'error': 'Invalid signature'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            # Process event only after verification
            event_type = event['type']
            event_data = event['data']['object']
            
            if event_type == 'checkout.session.completed':
                payment_logger.info(f'Checkout completed: {event_data.get("id")}')
                # ... handle payment
            
            elif event_type == 'charge.refunded':
                payment_logger.warning(f'Refund processed: {event_data.get("id")}')
                # ... handle refund
            
            return Response({'success': True})
        
        except Exception as e:
            payment_logger.error(f'Webhook processing error: {str(e)}')
            return Response(
                {'error': 'Processing failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        try:
            event = StripePaymentService.verify_webhook_signature(
                payload,
                sig_header,
                settings.STRIPE_WEBHOOK_SECRET
            )
            
            event_type = event['type']
            event_data = event['data']['object']
            
            logger.info(f"Stripe webhook received: {event_type}")
            
            if event_type == 'checkout.session.completed':
                _handle_checkout_completed(event_data)
            
            elif event_type == 'charge.succeeded':
                _handle_charge_succeeded(event_data)
            
            elif event_type == 'charge.failed':
                _handle_charge_failed(event_data)
            
            elif event_type == 'charge.refunded':
                _handle_charge_refunded(event_data)
            
            return Response({'received': True}, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Webhook error: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


def _handle_checkout_completed(session_data):
    """Handle checkout.session.completed webhook"""
    session_id = session_data['id']
    payment_intent = session_data.get('payment_intent')
    
    try:
        payment = Payment.objects.get(session_id=session_id)
        if payment.status != 'COMPLETED':
            payment.status = 'COMPLETED'
            payment.gateway_reference = payment_intent
            payment.save()
            
            # Update order status
            order = payment.order
            if order.status == 'PENDING':
                order.status = 'RECEIVED'
                order.save()
            
            logger.info(f"Payment completed via webhook: {payment.id}")
    except Payment.DoesNotExist:
        logger.warning(f"Payment not found for session: {session_id}")


def _handle_charge_succeeded(charge_data):
    """Handle charge.succeeded webhook"""
    metadata = charge_data.get('metadata', {})
    order_id = metadata.get('order_id')
    
    if order_id:
        try:
            payment = Payment.objects.get(order_id=order_id)
            payment.status = 'COMPLETED'
            payment.save()
            logger.info(f"Payment charge succeeded: {payment.id}")
        except Payment.DoesNotExist:
            pass


def _handle_charge_failed(charge_data):
    """Handle charge.failed webhook"""
    metadata = charge_data.get('metadata', {})
    order_id = metadata.get('order_id')
    
    if order_id:
        try:
            payment = Payment.objects.get(order_id=order_id)
            payment.status = 'FAILED'
            payment.save()
            logger.error(f"Payment charge failed: {payment.id}")
        except Payment.DoesNotExist:
            pass


def _handle_charge_refunded(charge_data):
    """Handle charge.refunded webhook"""
    metadata = charge_data.get('metadata', {})
    order_id = metadata.get('order_id')
    
    if order_id:
        try:
            payment = Payment.objects.get(order_id=order_id)
            payment.status = 'REFUNDED'
            payment.save()
            logger.info(f"Payment refunded via webhook: {payment.id}")
        except Payment.DoesNotExist:
            pass


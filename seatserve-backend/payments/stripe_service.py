"""
Stripe payment service integration
Handles checkout sessions, payment confirmation, and refunds
"""
import stripe
from decimal import Decimal
from django.conf import settings
from django.urls import reverse


# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripePaymentService:
    """Handle all Stripe payment operations"""
    
    @staticmethod
    def create_checkout_session(order, request=None):
        """
        Create a Stripe Checkout session for an order
        
        Args:
            order: Order instance
            request: Request object (for building absolute URLs)
            
        Returns:
            dict: Session data with session_id and client_secret
            
        Raises:
            stripe.error.StripeError: If Stripe API call fails
        """
        try:
            restaurant = order.restaurant
            
            # Prepare line items
            line_items = []
            for item in order.items.all():
                line_items.append({
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': item.menu_item.name,
                            'description': f"Table {order.table.number}" if order.table else "To-go",
                            'metadata': {
                                'restaurant_id': str(restaurant.id),
                                'order_id': str(order.id),
                            }
                        },
                        'unit_amount': int(item.price * 100),  # Convert to cents
                    },
                    'quantity': item.quantity,
                })
            
            # Build success/cancel URLs
            base_url = settings.FRONTEND_URL if hasattr(settings, 'FRONTEND_URL') else 'http://localhost:3000'
            success_url = f"{base_url}/order-status/{order.public_token}?session_id={{CHECKOUT_SESSION_ID}}"
            cancel_url = f"{base_url}/order/{restaurant.public_id}/{order.table.token if order.table else 'checkout'}"
            
            # Create session
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'order_id': str(order.id),
                    'restaurant_id': str(restaurant.id),
                    'customer_email': order.customer_email or '',
                },
                customer_email=order.customer_email,
            )
            
            return {
                'session_id': session.id,
                'client_secret': session.client_secret,
                'status': 'created'
            }
            
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe API error: {str(e)}")
    
    @staticmethod
    def confirm_payment(session_id):
        """
        Confirm payment status from Stripe session
        
        Args:
            session_id: Stripe Checkout Session ID
            
        Returns:
            dict: Session data with payment status
        """
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            
            return {
                'session_id': session.id,
                'payment_intent': session.payment_intent,
                'payment_status': session.payment_status,
                'customer_email': session.customer_email,
                'amount_total': Decimal(session.amount_total) / 100,  # Convert from cents
                'metadata': session.metadata,
            }
            
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to retrieve session: {str(e)}")
    
    @staticmethod
    def confirm_payment_intent(payment_intent_id):
        """
        Get payment intent details
        
        Args:
            payment_intent_id: Stripe Payment Intent ID
            
        Returns:
            dict: Payment intent details
        """
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            return {
                'id': intent.id,
                'status': intent.status,
                'amount': Decimal(intent.amount) / 100,
                'currency': intent.currency,
                'charges': [
                    {
                        'id': charge.id,
                        'amount': Decimal(charge.amount) / 100,
                        'status': charge.status,
                    }
                    for charge in intent.charges.data
                ]
            }
            
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to retrieve payment intent: {str(e)}")
    
    @staticmethod
    def refund_payment(payment_intent_id, amount=None):
        """
        Refund a payment
        
        Args:
            payment_intent_id: Stripe Payment Intent ID
            amount: Optional refund amount in dollars (None = full refund)
            
        Returns:
            dict: Refund details
        """
        try:
            refund_params = {
                'payment_intent': payment_intent_id,
            }
            
            if amount:
                # Convert to cents
                refund_params['amount'] = int(amount * 100)
            
            refund = stripe.Refund.create(**refund_params)
            
            return {
                'id': refund.id,
                'status': refund.status,
                'amount': Decimal(refund.amount) / 100,
                'reason': refund.reason,
                'metadata': refund.metadata,
            }
            
        except stripe.error.StripeError as e:
            raise Exception(f"Refund failed: {str(e)}")
    
    @staticmethod
    def verify_webhook_signature(payload, sig_header, endpoint_secret):
        """
        Verify Stripe webhook signature
        
        Args:
            payload: Raw request body
            sig_header: Stripe-Signature header
            endpoint_secret: Webhook endpoint secret from Stripe dashboard
            
        Returns:
            dict: Parsed event data
            
        Raises:
            Exception: If signature verification fails
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
            return event
            
        except ValueError as e:
            raise Exception(f"Invalid payload: {str(e)}")
        except stripe.error.SignatureVerificationError as e:
            raise Exception(f"Invalid signature: {str(e)}")
    
    @staticmethod
    def get_webhook_event(event_id):
        """Retrieve webhook event details"""
        try:
            event = stripe.Event.retrieve(event_id)
            return event
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to retrieve event: {str(e)}")

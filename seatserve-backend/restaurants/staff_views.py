"""
Staff management views
Handles staff member invitation, permission management, and role updates
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import logging

from restaurants.models import StaffMember, Restaurant, StaffPermission
from restaurants.serializers import (
    StaffMemberSerializer, StaffMemberCreateSerializer, StaffMemberUpdateSerializer,
    StaffPermissionSerializer
)
from restaurants.permissions import IsRestaurantOwner

logger = logging.getLogger(__name__)


class StaffMemberViewSet(viewsets.ModelViewSet):
    """Manage restaurant staff members"""
    serializer_class = StaffMemberSerializer
    permission_classes = (IsAuthenticated, IsRestaurantOwner)

    def get_queryset(self):
        """Get staff members for current user's restaurant"""
        restaurant = Restaurant.objects.filter(owner=self.request.user).first()
        if restaurant:
            return StaffMember.objects.filter(restaurant=restaurant).order_by('-created_at')
        return StaffMember.objects.none()

    def list(self, request, *args, **kwargs):
        """List all staff members"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        # Add summary
        active_count = queryset.filter(status='ACTIVE').count()
        inactive_count = queryset.filter(status='INACTIVE').count()
        pending_invitations = queryset.filter(status='ACTIVE', invitation_accepted_at__isnull=True).count()
        
        return Response({
            'staff_members': serializer.data,
            'summary': {
                'total': queryset.count(),
                'active': active_count,
                'inactive': inactive_count,
                'pending_invitations': pending_invitations,
            }
        })

    def create(self, request, *args, **kwargs):
        """Invite a new staff member"""
        serializer = StaffMemberCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        restaurant = Restaurant.objects.filter(owner=request.user).first()
        if not restaurant:
            return Response(
                {'detail': 'Restaurant not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if staff member already exists
        if StaffMember.objects.filter(restaurant=restaurant, email=serializer.validated_data['email']).exists():
            return Response(
                {'detail': 'Staff member with this email already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create staff member
        staff_member = StaffMember.objects.create(
            restaurant=restaurant,
            name=serializer.validated_data['name'],
            email=serializer.validated_data['email'],
            phone=serializer.validated_data.get('phone', ''),
            role=serializer.validated_data['role'],
            can_view_orders=serializer.validated_data.get('can_view_orders', True),
            can_update_orders=serializer.validated_data.get('can_update_orders', False),
            can_view_menu=serializer.validated_data.get('can_view_menu', True),
            can_edit_menu=serializer.validated_data.get('can_edit_menu', False),
            can_view_tables=serializer.validated_data.get('can_view_tables', True),
            can_edit_tables=serializer.validated_data.get('can_edit_tables', False),
            can_view_analytics=serializer.validated_data.get('can_view_analytics', False),
            can_manage_staff=serializer.validated_data.get('can_manage_staff', False),
        )
        
        # Generate invitation token
        staff_member.generate_invitation_token()
        staff_member.save()
        
        # Send invitation email (async in production)
        self._send_invitation_email(staff_member, request)
        
        logger.info(f"Staff member invited: {staff_member.id} - {staff_member.email}")
        
        return Response(
            StaffMemberSerializer(staff_member).data,
            status=status.HTTP_201_CREATED
        )

    def partial_update(self, request, pk=None):
        """Update staff member (permissions, role, status)"""
        staff_member = self.get_object()
        serializer = StaffMemberUpdateSerializer(staff_member, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Staff member updated: {staff_member.id}")
            return Response(StaffMemberSerializer(staff_member).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail='pk', methods=['post'])
    def resend_invitation(self, request, pk=None):
        """Resend invitation to staff member"""
        staff_member = self.get_object()
        
        if not staff_member.is_invited:
            return Response(
                {'detail': 'Staff member has already accepted the invitation'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Regenerate and resend
        staff_member.generate_invitation_token()
        staff_member.save()
        
        self._send_invitation_email(staff_member, request)
        
        return Response({
            'message': 'Invitation resent',
            'staff_member': StaffMemberSerializer(staff_member).data,
        })

    @action(detail='pk', methods=['post'])
    def suspend(self, request, pk=None):
        """Suspend staff member"""
        staff_member = self.get_object()
        staff_member.status = 'SUSPENDED'
        staff_member.save()
        
        logger.info(f"Staff member suspended: {staff_member.id}")
        return Response({
            'message': 'Staff member suspended',
            'staff_member': StaffMemberSerializer(staff_member).data,
        })

    @action(detail='pk', methods=['post'])
    def activate(self, request, pk=None):
        """Activate staff member"""
        staff_member = self.get_object()
        staff_member.status = 'ACTIVE'
        staff_member.save()
        
        logger.info(f"Staff member activated: {staff_member.id}")
        return Response({
            'message': 'Staff member activated',
            'staff_member': StaffMemberSerializer(staff_member).data,
        })

    @action(detail='pk', methods=['delete'])
    def remove(self, request, pk=None):
        """Remove staff member"""
        staff_member = self.get_object()
        staff_member.delete()
        
        logger.info(f"Staff member removed: {staff_member.id}")
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def by_role(self, request):
        """Get staff members grouped by role"""
        restaurant = Restaurant.objects.filter(owner=request.user).first()
        if not restaurant:
            return Response(
                {'detail': 'Restaurant not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        roles = {}
        for role_choice in StaffMember.ROLE_CHOICES:
            role_key = role_choice[0]
            staff_list = StaffMember.objects.filter(
                restaurant=restaurant, role=role_key
            ).values('id', 'name', 'email', 'status')
            roles[role_key] = list(staff_list)
        
        return Response(roles)

    def _send_invitation_email(self, staff_member, request):
        """Send invitation email to staff member"""
        try:
            invitation_url = f"{settings.FRONTEND_URL}/staff/accept-invitation/{staff_member.invitation_token}"
            
            subject = f"Join {staff_member.restaurant.name} as Staff"
            message = f"""
            Hello {staff_member.name},
            
            You have been invited to join {staff_member.restaurant.name} as a {staff_member.get_role_display()}.
            
            Please click the link below to accept the invitation:
            {invitation_url}
            
            Best regards,
            {staff_member.restaurant.name}
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [staff_member.email],
                fail_silently=True,
            )
            
            logger.info(f"Invitation email sent to {staff_member.email}")
        except Exception as e:
            logger.error(f"Failed to send invitation email: {str(e)}")

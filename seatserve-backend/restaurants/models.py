import uuid
import json
from django.db import models
from django.utils.timezone import now, timedelta
from accounts.models import User


class Plan(models.Model):
    BILLING_PERIOD_CHOICES = (
        ('MONTH', 'Monthly'),
        ('YEAR', 'Yearly'),
    )

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    billing_period = models.CharField(max_length=10, choices=BILLING_PERIOD_CHOICES, default='MONTH')
    max_tables = models.IntegerField(default=10)
    max_menu_items = models.IntegerField(default=100)
    features = models.JSONField(default=dict)  # e.g., {"qr_ordering": true, "live_dashboard": true}
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'restaurants_plan'
        ordering = ['price']

    def __str__(self):
        return f'{self.name} ({self.price}/{self.billing_period})'


class Restaurant(models.Model):
    id = models.BigAutoField(primary_key=True)
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='restaurant')
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField()
    
    logo_url = models.URLField(blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'restaurants_restaurant'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def active_subscription(self):
        """Get the currently active subscription"""
        return self.subscriptions.filter(
            status='ACTIVE',
            end_date__gte=now()
        ).first()


class RestaurantSubscription(models.Model):
    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('EXPIRED', 'Expired'),
        ('CANCELLED', 'Cancelled'),
    )

    id = models.BigAutoField(primary_key=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    payment_reference = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'restaurants_subscription'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.restaurant.name} - {self.plan.name}'

    def is_valid(self):
        return self.status == 'ACTIVE' and self.end_date >= now()


class Table(models.Model):
    id = models.BigAutoField(primary_key=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='tables')
    name = models.CharField(max_length=100)  # e.g., "T1", "Balcony-3"
    token = models.CharField(max_length=255, unique=True, db_index=True)  # unique per table
    qr_code_url = models.URLField(blank=True)
    
    capacity = models.IntegerField(default=4)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'restaurants_table'
        unique_together = ('restaurant', 'name')
        ordering = ['name']

    def __str__(self):
        return f'{self.restaurant.name} - {self.name}'

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = str(uuid.uuid4())
        super().save(*args, **kwargs)


class StaffMember(models.Model):
    """Staff members of a restaurant"""
    
    ROLE_CHOICES = (
        ('MANAGER', 'Manager'),
        ('CHEF', 'Chef'),
        ('WAITER', 'Waiter'),
        ('CASHIER', 'Cashier'),
        ('DELIVERY', 'Delivery Executive'),
    )
    
    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('SUSPENDED', 'Suspended'),
    )

    id = models.BigAutoField(primary_key=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='staff_members')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='staff_positions')
    
    email = models.EmailField()  # Staff email (if not registered yet)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True)
    
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    
    # Permissions
    can_view_orders = models.BooleanField(default=True)
    can_update_orders = models.BooleanField(default=False)  # Update order status
    can_view_menu = models.BooleanField(default=True)
    can_edit_menu = models.BooleanField(default=False)
    can_view_tables = models.BooleanField(default=True)
    can_edit_tables = models.BooleanField(default=False)
    can_view_analytics = models.BooleanField(default=False)
    can_manage_staff = models.BooleanField(default=False)  # Only Manager/Admin
    
    # Invitation tracking
    invitation_token = models.CharField(max_length=255, unique=True, db_index=True, blank=True)
    invitation_sent_at = models.DateTimeField(null=True, blank=True)
    invitation_accepted_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'restaurants_staffmember'
        unique_together = ('restaurant', 'email')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['restaurant', 'status']),
            models.Index(fields=['invitation_token']),
        ]

    def __str__(self):
        return f'{self.restaurant.name} - {self.name} ({self.role})'
    
    @property
    def is_invited(self):
        """Check if staff member has been invited but not accepted"""
        return self.invitation_token and not self.invitation_accepted_at
    
    @property
    def is_active_user(self):
        """Check if staff member has accepted invitation and is active"""
        return self.user is not None and self.status == 'ACTIVE'
    
    def generate_invitation_token(self):
        """Generate a unique invitation token"""
        import uuid
        self.invitation_token = str(uuid.uuid4())
        from django.utils import timezone
        self.invitation_sent_at = timezone.now()
        return self.invitation_token
    
    def accept_invitation(self, user):
        """Accept the invitation and link to user"""
        from django.utils import timezone
        self.user = user
        self.invitation_accepted_at = timezone.now()
        self.save()


class StaffPermission(models.Model):
    """Granular permissions for staff members (optional, for complex scenarios)"""
    
    id = models.BigAutoField(primary_key=True)
    staff_member = models.ForeignKey(StaffMember, on_delete=models.CASCADE, related_name='permissions')
    permission_name = models.CharField(max_length=100)  # e.g., "edit_order_status", "delete_menu_item"
    allowed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'restaurants_staffpermission'
        unique_together = ('staff_member', 'permission_name')

    def __str__(self):
        return f'{self.staff_member.name} - {self.permission_name}'

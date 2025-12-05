from rest_framework import serializers
from django.utils.timezone import now, timedelta
from restaurants.models import Plan, Restaurant, RestaurantSubscription, Table, StaffMember, StaffPermission


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ('id', 'name', 'description', 'price', 'billing_period', 'max_tables', 
                  'max_menu_items', 'features', 'is_active')
        read_only_fields = ('id',)


class RestaurantSerializer(serializers.ModelSerializer):
    owner_email = serializers.CharField(source='owner.email', read_only=True)
    active_subscription = serializers.SerializerMethodField()

    class Meta:
        model = Restaurant
        fields = ('id', 'public_id', 'name', 'description', 'address', 'city', 'country', 
                  'phone', 'email', 'logo_url', 'owner_email', 'is_active', 'active_subscription',
                  'created_at', 'updated_at')
        read_only_fields = ('id', 'public_id', 'owner_email', 'created_at', 'updated_at')

    def get_active_subscription(self, obj):
        subscription = obj.active_subscription
        if subscription:
            return RestaurantSubscriptionSerializer(subscription).data
        return None


class RestaurantCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20, required=False)
    city = serializers.CharField(max_length=100, required=False)
    country = serializers.CharField(max_length=100, required=False)
    address = serializers.CharField(required=False)
    
    def create(self, validated_data):
        # This is typically called by the accounts registration flow
        # The user is already created at that point
        pass


class RestaurantSubscriptionSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    plan_details = PlanSerializer(source='plan', read_only=True)

    class Meta:
        model = RestaurantSubscription
        fields = ('id', 'restaurant', 'plan', 'plan_name', 'plan_details', 'status', 
                  'start_date', 'end_date', 'payment_reference', 'created_at')
        read_only_fields = ('id', 'created_at')


class TableSerializer(serializers.ModelSerializer):
    qr_code_url = serializers.SerializerMethodField()

    class Meta:
        model = Table
        fields = ('id', 'restaurant', 'name', 'token', 'qr_code_url', 'capacity', 
                  'is_active', 'created_at', 'updated_at')
        read_only_fields = ('id', 'restaurant', 'token', 'created_at', 'updated_at')

    def get_qr_code_url(self, obj):
        if obj.qr_code_url:
            return obj.qr_code_url
        # Generate QR code URL if not already stored
        # This would typically be generated and stored during creation
        return None


class StaffPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffPermission
        fields = ('id', 'permission_name', 'allowed')


class StaffMemberSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    permissions = StaffPermissionSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = StaffMember
        fields = (
            'id', 'restaurant', 'user', 'user_email', 'email', 'name', 'phone', 
            'role', 'role_display', 'status', 'status_display',
            'can_view_orders', 'can_update_orders', 'can_view_menu', 'can_edit_menu',
            'can_view_tables', 'can_edit_tables', 'can_view_analytics', 'can_manage_staff',
            'is_invited', 'is_active_user', 'invitation_sent_at', 'invitation_accepted_at',
            'permissions', 'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'restaurant', 'user', 'user_email', 'invitation_token',
            'is_invited', 'is_active_user', 'invitation_sent_at', 'invitation_accepted_at',
            'created_at', 'updated_at'
        )


class StaffMemberCreateSerializer(serializers.Serializer):
    """Serializer for inviting new staff members"""
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20, required=False)
    role = serializers.ChoiceField(choices=[
        ('MANAGER', 'Manager'),
        ('CHEF', 'Chef'),
        ('WAITER', 'Waiter'),
        ('CASHIER', 'Cashier'),
        ('DELIVERY', 'Delivery Executive'),
    ])
    
    # Permissions
    can_view_orders = serializers.BooleanField(default=True)
    can_update_orders = serializers.BooleanField(default=False)
    can_view_menu = serializers.BooleanField(default=True)
    can_edit_menu = serializers.BooleanField(default=False)
    can_view_tables = serializers.BooleanField(default=True)
    can_edit_tables = serializers.BooleanField(default=False)
    can_view_analytics = serializers.BooleanField(default=False)
    can_manage_staff = serializers.BooleanField(default=False)


class StaffMemberUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffMember
        fields = (
            'name', 'phone', 'role', 'status',
            'can_view_orders', 'can_update_orders', 'can_view_menu', 'can_edit_menu',
            'can_view_tables', 'can_edit_tables', 'can_view_analytics', 'can_manage_staff',
        )

"""
Plan enforcement service
Validates restaurant operations against their subscription plan limits
"""
from django.utils.timezone import now
from restaurants.models import Restaurant, RestaurantSubscription
from menu.models import MenuItem
from restaurants.models import Table


class PlanEnforcementService:
    """Service for checking and enforcing plan limits"""
    
    @staticmethod
    def get_active_subscription(restaurant):
        """Get active subscription for restaurant"""
        return restaurant.subscriptions.filter(
            status='ACTIVE',
            end_date__gte=now()
        ).select_related('plan').first()
    
    @staticmethod
    def get_remaining_tables(restaurant):
        """Get remaining table quota for restaurant"""
        subscription = PlanEnforcementService.get_active_subscription(restaurant)
        if not subscription:
            return 0
        
        plan = subscription.plan
        current_tables = restaurant.tables.count()
        return max(0, plan.max_tables - current_tables)
    
    @staticmethod
    def get_remaining_menu_items(restaurant):
        """Get remaining menu item quota for restaurant"""
        subscription = PlanEnforcementService.get_active_subscription(restaurant)
        if not subscription:
            return 0
        
        plan = subscription.plan
        current_items = restaurant.menu_items.count()
        return max(0, plan.max_menu_items - current_items)
    
    @staticmethod
    def can_add_table(restaurant):
        """Check if restaurant can add a new table"""
        subscription = PlanEnforcementService.get_active_subscription(restaurant)
        
        if not subscription:
            raise ValueError("No active subscription")
        
        plan = subscription.plan
        current_tables = restaurant.tables.count()
        
        if current_tables >= plan.max_tables:
            return False, f"Plan limit reached: {plan.max_tables} tables allowed"
        
        return True, None
    
    @staticmethod
    def can_add_menu_item(restaurant):
        """Check if restaurant can add a new menu item"""
        subscription = PlanEnforcementService.get_active_subscription(restaurant)
        
        if not subscription:
            raise ValueError("No active subscription")
        
        plan = subscription.plan
        current_items = restaurant.menu_items.count()
        
        if current_items >= plan.max_menu_items:
            return False, f"Plan limit reached: {plan.max_menu_items} menu items allowed"
        
        return True, None
    
    @staticmethod
    def has_feature(restaurant, feature_name):
        """Check if restaurant's plan has a specific feature"""
        subscription = PlanEnforcementService.get_active_subscription(restaurant)
        
        if not subscription:
            return False
        
        plan = subscription.plan
        features = plan.features or {}
        
        return features.get(feature_name, False)
    
    @staticmethod
    def get_plan_info(restaurant):
        """Get detailed plan information"""
        subscription = PlanEnforcementService.get_active_subscription(restaurant)
        
        if not subscription:
            return {
                'status': 'no_subscription',
                'plan': None,
                'end_date': None,
                'tables_used': 0,
                'tables_available': 0,
                'menu_items_used': 0,
                'menu_items_available': 0,
                'features': {}
            }
        
        plan = subscription.plan
        tables_used = restaurant.tables.count()
        menu_items_used = restaurant.menu_items.count()
        
        return {
            'status': subscription.status,
            'plan': {
                'id': plan.id,
                'name': plan.name,
                'price': float(plan.price),
                'billing_period': plan.billing_period,
                'features': plan.features,
            },
            'end_date': subscription.end_date.isoformat(),
            'tables_used': tables_used,
            'tables_available': plan.max_tables,
            'menu_items_used': menu_items_used,
            'menu_items_available': plan.max_menu_items,
            'usage_percent': {
                'tables': round((tables_used / plan.max_tables) * 100, 1),
                'menu_items': round((menu_items_used / plan.max_menu_items) * 100, 1),
            }
        }
    
    @staticmethod
    def is_subscription_active(restaurant):
        """Check if restaurant has an active subscription"""
        subscription = PlanEnforcementService.get_active_subscription(restaurant)
        return subscription is not None

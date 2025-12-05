"""
Seed initial data for SeatServe
"""
from django.core.management.base import BaseCommand
from restaurants.models import Plan
from django.utils.timezone import now


class Command(BaseCommand):
    help = 'Seed initial data (plans)'

    def handle(self, *args, **options):
        # Create default plans
        plans_data = [
            {
                'name': 'Basic',
                'description': 'Perfect for small restaurants',
                'price': 9.99,
                'billing_period': 'MONTH',
                'max_tables': 5,
                'max_menu_items': 50,
                'features': {
                    'qr_ordering': True,
                    'live_dashboard': True,
                    'menu_management': True,
                    'online_payments': False,
                }
            },
            {
                'name': 'Standard',
                'description': 'For growing restaurants',
                'price': 24.99,
                'billing_period': 'MONTH',
                'max_tables': 20,
                'max_menu_items': 200,
                'features': {
                    'qr_ordering': True,
                    'live_dashboard': True,
                    'menu_management': True,
                    'online_payments': True,
                    'staff_roles': True,
                }
            },
            {
                'name': 'Pro',
                'description': 'For large restaurants & chains',
                'price': 49.99,
                'billing_period': 'MONTH',
                'max_tables': 100,
                'max_menu_items': 1000,
                'features': {
                    'qr_ordering': True,
                    'live_dashboard': True,
                    'menu_management': True,
                    'online_payments': True,
                    'staff_roles': True,
                    'analytics': True,
                    'delivery_integration': True,
                }
            },
        ]

        for plan_data in plans_data:
            plan, created = Plan.objects.get_or_create(
                name=plan_data['name'],
                defaults=plan_data
            )
            status = 'Created' if created else 'Already exists'
            self.stdout.write(self.style.SUCCESS(f'{status}: {plan.name}'))

        self.stdout.write(self.style.SUCCESS('Seeding completed!'))

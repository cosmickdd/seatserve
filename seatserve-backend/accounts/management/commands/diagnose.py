"""
Django management command to run production diagnostics
Usage: python manage.py diagnose
"""

from django.core.management.base import BaseCommand
from config.diagnostic import ProductionDiagnostic


class Command(BaseCommand):
    help = 'Run comprehensive production diagnostics for SeatServe'

    def handle(self, *args, **options):
        diagnostic = ProductionDiagnostic()
        success = diagnostic.run_all()
        
        if not success:
            self.stdout.write(
                self.style.ERROR('Diagnostics completed with errors!')
            )
            exit(1)
        else:
            self.stdout.write(
                self.style.SUCCESS('All diagnostics passed!')
            )

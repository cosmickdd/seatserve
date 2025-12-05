from django.db import models
from django.utils import timezone


class Payment(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
        ('REFUND_PENDING', 'Refund Pending'),
    )

    PAYMENT_METHOD_CHOICES = (
        ('STRIPE', 'Stripe'),
        ('RAZORPAY', 'Razorpay'),
        ('CASH', 'Cash'),
    )

    id = models.BigAutoField(primary_key=True)
    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='payment')
    restaurant = models.ForeignKey('restaurants.Restaurant', on_delete=models.CASCADE, related_name='payments')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, default='STRIPE')
    gateway_reference = models.CharField(max_length=255, blank=True, db_index=True)  # Stripe transaction ID
    session_id = models.CharField(max_length=255, blank=True)  # Stripe Checkout Session ID
    
    # Refund tracking
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    refund_reason = models.TextField(blank=True)
    refund_gateway_reference = models.CharField(max_length=255, blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments_payment'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['restaurant', '-created_at']),
            models.Index(fields=['gateway_reference']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f'Payment {self.id} - {self.get_status_display()} (${self.amount})'
    
    @property
    def is_refundable(self):
        """Check if payment can be refunded"""
        return self.status == 'COMPLETED' and (self.amount - self.refund_amount) > 0
    
    def refund(self, amount=None):
        """Mark as refunded - actual gateway refund handled in views"""
        if not self.is_refundable:
            raise ValueError(f"Payment cannot be refunded. Status: {self.status}")
        
        refund_amount = amount or self.amount
        if refund_amount > (self.amount - self.refund_amount):
            raise ValueError("Refund amount exceeds available balance")
        
        self.refund_amount += refund_amount
        self.status = 'REFUND_PENDING'
        self.save()

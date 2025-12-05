import uuid
from django.db import models
from django.utils.timezone import now, timedelta
from restaurants.models import Restaurant, Table
from menu.models import MenuItem


class Order(models.Model):
    STATUS_CHOICES = (
        ('RECEIVED', 'Received'),
        ('IN_KITCHEN', 'In Kitchen'),
        ('READY_TO_SERVE', 'Ready to Serve'),
        ('SERVED', 'Served'),
        ('CANCELLED', 'Cancelled'),
    )

    PAYMENT_STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
    )

    id = models.BigAutoField(primary_key=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='orders')
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    
    public_token = models.CharField(max_length=255, unique=True, db_index=True)  # for guest access
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='RECEIVED')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estimated_time_minutes = models.IntegerField(default=20)
    
    customer_note = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders_order'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['restaurant', '-created_at']),
            models.Index(fields=['public_token']),
        ]

    def __str__(self):
        return f'Order {self.public_token} - {self.restaurant.name}'

    def save(self, *args, **kwargs):
        if not self.public_token:
            self.public_token = str(uuid.uuid4())
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    id = models.BigAutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.PROTECT)
    
    quantity = models.IntegerField(default=1)
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2)  # price snapshot
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'orders_item'

    def __str__(self):
        return f'{self.menu_item.name} x {self.quantity}'

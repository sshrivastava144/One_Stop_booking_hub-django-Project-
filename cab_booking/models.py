# cab_booking/models.py
from django.db import models
from django.conf import settings
import uuid

class CabService(models.Model):
    """Different cab service providers (Ola, Uber, etc.)"""
    name = models.CharField(max_length=100)
    base_fare = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)
    per_km_rate = models.DecimalField(max_digits=10, decimal_places=2, default=10.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class CabType(models.Model):
    """Different types of cabs (Mini, Sedan, SUV, etc.)"""
    CAB_CHOICES = [
        ('mini', 'Mini'),
        ('sedan', 'Sedan'),
        ('suv', 'SUV'),
        ('luxury', 'Luxury'),
    ]
    
    name = models.CharField(max_length=20, choices=CAB_CHOICES)
    price_multiplier = models.DecimalField(max_digits=3, decimal_places=2, default=1.00)
    capacity = models.IntegerField(default=4)

    def __str__(self):
        return self.get_name_display()

class Driver(models.Model):
    """Driver information"""
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    vehicle_number = models.CharField(max_length=20)
    cab_service = models.ForeignKey(CabService, on_delete=models.CASCADE)
    vehicle_type = models.ForeignKey(CabType, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)

    def __str__(self):
        return f"{self.name} - {self.vehicle_number}"

class CabBooking(models.Model):
    """Main booking model"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    booking_id = models.CharField(max_length=20, unique=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cab_service = models.ForeignKey(CabService, on_delete=models.CASCADE)
    cab_type = models.ForeignKey(CabType, on_delete=models.CASCADE)
    
    pickup_location = models.CharField(max_length=200)
    drop_location = models.CharField(max_length=200)
    pickup_time = models.DateTimeField()
    
    distance_km = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estimated_fare = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    final_fare = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    driver_name = models.CharField(max_length=100, blank=True)
    driver_phone = models.CharField(max_length=15, blank=True)
    vehicle_number = models.CharField(max_length=20, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rating = models.IntegerField(null=True, blank=True, choices=[(i, i) for i in range(1, 6)])
    feedback = models.TextField(blank=True)
    special_instructions = models.TextField(blank=True)  # Add this missing field
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.booking_id:
            self.booking_id = f"CAB{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.booking_id} - {self.user.username}"

class FareCalculation(models.Model):
    """Store fare calculation details"""
    booking = models.OneToOneField(CabBooking, on_delete=models.CASCADE)
    base_fare = models.DecimalField(max_digits=10, decimal_places=2)
    distance_fare = models.DecimalField(max_digits=10, decimal_places=2)
    surge_multiplier = models.DecimalField(max_digits=3, decimal_places=2, default=1.00)
    total_fare = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Fare for {self.booking.booking_id}"
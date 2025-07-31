# cab_booking/admin.py - Use this after models are working
from django.contrib import admin
from .models import CabService, CabType, CabBooking, Driver, FareCalculation

@admin.register(CabService)
class CabServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_fare', 'per_km_rate', 'is_active']
    list_filter = ['is_active']

@admin.register(CabType)
class CabTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'price_multiplier', 'capacity']

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'vehicle_number', 'cab_service', 'is_available', 'rating']
    list_filter = ['cab_service', 'is_available', 'vehicle_type']

@admin.register(CabBooking)
class CabBookingAdmin(admin.ModelAdmin):
    list_display = ['booking_id', 'user', 'cab_service', 'status', 'estimated_fare', 'created_at']
    list_filter = ['status', 'cab_service', 'created_at']
    search_fields = ['booking_id', 'user__username']
    readonly_fields = ['booking_id', 'created_at', 'updated_at']

@admin.register(FareCalculation)
class FareCalculationAdmin(admin.ModelAdmin):
    list_display = ['booking', 'total_fare', 'surge_multiplier', 'created_at']
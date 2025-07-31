from django.urls import path
from . import views

app_name = 'cab_booking'

urlpatterns = [
    # Main pages
    
    path('', views.cab_booking_home, name='home'),
    path('book/', views.book_cab, name='book_cab'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('fare-calculator/', views.fare_calculator, name='fare_calculator'),
    
    # Booking specific pages
    path('booking/<str:booking_id>/', views.booking_detail, name='booking_detail'),
    path('booking/<str:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('booking/<str:booking_id>/track/', views.track_booking, name='track_booking'),
    
    # AJAX endpoints
    path('ajax/calculate-fare/', views.calculate_fare_ajax, name='calculate_fare_ajax'),
    path('api/booking/<str:booking_id>/status/', views.api_booking_status, name='api_booking_status'),
]
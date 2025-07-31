

# cab_booking/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import CabBooking, CabService, CabType, Driver, FareCalculation
from .forms import CabBookingForm, FareCalculatorForm, BookingSearchForm, RatingForm
import json
import random
from decimal import Decimal

@login_required
def cab_booking_home(request):
    """Main cab booking page"""
    recent_bookings = CabBooking.objects.filter(user=request.user)[:3]
    cab_services = CabService.objects.filter(is_active=True)
    cab_types = CabType.objects.all()
    
    context = {
        'recent_bookings': recent_bookings,
        'cab_services': cab_services,
        'cab_types': cab_types,
    }
    return render(request, 'cab_booking/home.html', context)

@login_required
def book_cab(request):
    """Book a new cab"""
    if request.method == 'POST':
        form = CabBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            
            # Calculate estimated fare
            distance = calculate_distance(
                form.cleaned_data['pickup_location'],
                form.cleaned_data['drop_location']
            )
            booking.distance_km = distance
            booking.estimated_fare = calculate_fare(
                booking.cab_service,
                booking.cab_type,
                distance
            )
            
            booking.save()
            messages.success(request, f'Cab booked successfully! Booking ID: {booking.booking_id}')
            return redirect('cab_booking:booking_detail', booking_id=booking.booking_id)
    else:
        form = CabBookingForm()
    
    return render(request, 'cab_booking/book_cab.html', {'form': form})

@login_required
def booking_detail(request, booking_id):
    """View booking details"""
    booking = get_object_or_404(CabBooking, booking_id=booking_id, user=request.user)
    
    # Handle rating form
    if request.method == 'POST' and booking.status == 'completed':
        rating_form = RatingForm(request.POST, instance=booking)
        if rating_form.is_valid():
            rating_form.save()
            messages.success(request, 'Thank you for your feedback!')
            return redirect('cab_booking:booking_detail', booking_id=booking_id)
    else:
        rating_form = RatingForm(instance=booking)
    
    context = {
        'booking': booking,
        'rating_form': rating_form,
    }
    return render(request, 'cab_booking/booking_detail.html', context)

@login_required
def my_bookings(request):
    """List all user bookings with search/filter"""
    bookings_list = CabBooking.objects.filter(user=request.user)
    search_form = BookingSearchForm(request.GET)
    
    if search_form.is_valid():
        booking_id = search_form.cleaned_data.get('booking_id')
        status = search_form.cleaned_data.get('status')
        date_from = search_form.cleaned_data.get('date_from')
        date_to = search_form.cleaned_data.get('date_to')
        
        if booking_id:
            bookings_list = bookings_list.filter(booking_id__icontains=booking_id)
        if status:
            bookings_list = bookings_list.filter(status=status)
        if date_from:
            bookings_list = bookings_list.filter(created_at__date__gte=date_from)
        if date_to:
            bookings_list = bookings_list.filter(created_at__date__lte=date_to)
    
    paginator = Paginator(bookings_list, 10)
    page_number = request.GET.get('page')
    bookings = paginator.get_page(page_number)
    
    context = {
        'bookings': bookings,
        'search_form': search_form,
    }
    return render(request, 'cab_booking/my_bookings.html', context)

@login_required
def cancel_booking(request, booking_id):
    """Cancel a booking"""
    booking = get_object_or_404(CabBooking, booking_id=booking_id, user=request.user)
    
    if booking.status in ['pending', 'confirmed']:
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Booking cancelled successfully!')
    else:
        messages.error(request, 'Cannot cancel this booking at current status.')
    
    return redirect('cab_booking:booking_detail', booking_id=booking_id)

def calculate_fare_ajax(request):
    """AJAX endpoint for fare calculation"""
    if request.method == 'GET':
        pickup = request.GET.get('pickup')
        drop = request.GET.get('drop')
        service_id = request.GET.get('service_id')
        type_id = request.GET.get('type_id')
        
        try:
            service = CabService.objects.get(id=service_id)
            cab_type = CabType.objects.get(id=type_id)
            
            # Calculate distance (mock calculation)
            distance = calculate_distance(pickup, drop)
            fare = calculate_fare(service, cab_type, distance)
            
            return JsonResponse({
                'success': True,
                'distance': float(distance),
                'fare': float(fare),
                'service': service.name,
                'type': cab_type.get_name_display()
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def fare_calculator(request):
    """Standalone fare calculator page"""
    form = FareCalculatorForm()
    context = {'form': form}
    return render(request, 'cab_booking/fare_calculator.html', context)

@login_required
def track_booking(request, booking_id):
    """Real-time booking tracking"""
    booking = get_object_or_404(CabBooking, booking_id=booking_id, user=request.user)
    
    # Simulate real-time updates (in real app, this would connect to actual tracking)
    tracking_data = {
        'booking': booking,
        'driver_location': {
            'lat': 23.2599 + random.uniform(-0.01, 0.01),
            'lng': 77.4126 + random.uniform(-0.01, 0.01)
        },
        'estimated_arrival': '5-10 minutes'
    }
    
    return render(request, 'cab_booking/track_booking.html', tracking_data)

# Utility functions
def calculate_distance(pickup, drop):
    """Calculate distance between two locations (mock implementation)"""
    # In real implementation, use Google Maps API or similar
    # For now, return a random distance between 5-50 km
    return Decimal(str(random.uniform(5, 50)))

def calculate_fare(cab_service, cab_type, distance_km):
    """Calculate fare based on service, type and distance"""
    base_fare = cab_service.base_fare
    per_km_rate = cab_service.per_km_rate
    type_multiplier = cab_type.price_multiplier
    
    # Basic calculation: base fare + (distance * per km rate * type multiplier)
    fare = base_fare + (distance_km * per_km_rate * type_multiplier)
    
    # Add some surge pricing simulation (random between 1.0 to 1.5)
    surge_multiplier = Decimal(str(random.uniform(1.0, 1.5)))
    final_fare = fare * surge_multiplier
    
    return round(final_fare, 2)

def get_available_drivers(cab_service, cab_type):
    """Get available drivers for given service and type"""
    return Driver.objects.filter(
        cab_service=cab_service,
        vehicle_type=cab_type,
        is_available=True
    )

# API endpoints for mobile/frontend integration
@login_required
def api_booking_status(request, booking_id):
    """API endpoint for booking status"""
    try:
        booking = CabBooking.objects.get(booking_id=booking_id, user=request.user)
        return JsonResponse({
            'booking_id': booking.booking_id,
            'status': booking.status,
            'driver_name': booking.driver_name,
            'driver_phone': booking.driver_phone,
            'vehicle_number': booking.vehicle_number,
            'estimated_fare': float(booking.estimated_fare)
        })
    except CabBooking.DoesNotExist:
        return JsonResponse({'error': 'Booking not found'}, status=404)
    




    
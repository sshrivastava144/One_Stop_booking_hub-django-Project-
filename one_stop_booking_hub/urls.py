from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),  # Root URL goes to accounts
    path('accounts/', include('accounts.urls')),  # Also accessible via /accounts/
    path('cab-booking/', include('cab_booking.urls')),  # Cab booking URLs
    path('sabji-market/', include('sabji_market.urls')),  # Sabji market URLs
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
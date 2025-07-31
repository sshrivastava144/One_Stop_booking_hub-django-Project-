from django.urls import path
from . import views

app_name = 'accounts'  # This is crucial for namespacing

urlpatterns = [
    path('', views.home_view, name='home'),  # Root path - home page
    path('login/', views.login_view, name='login'),  # Login page
    path('register/', views.register_view, name='register'),  # Registration page
    path('logout/', views.logout_view, name='logout'),  # Logout
    path('profile/', views.profile_view, name='profile'),  # User profile
]
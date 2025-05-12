# airline/urls.py
from django.contrib import admin
# Make sure 'include' is imported
from django.urls import path, include
from flights import views as flights_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # --- API URLs ---
    # Include URLs from flights/api_urls.py under the /api/ prefix
    path('api/', include('flights.api_urls')),
    # Include DRF's login/logout views for the browsable API
    path('api-auth/', include('rest_framework.urls')), # ADD THIS LINE

    # --- Web Page URLs ---
    path("", flights_views.index, name="index"),
    # path('index/', flights_views.index, name='index_alias'), # Consider removing if '/' serves index
    path('flights/airport/<int:airport_id>/', flights_views.airport, name='airport_details'),
    path('booking/confirmation/<str:booking_code>/', flights_views.booking_confirmation, name='booking_confirmation'),
    path('flights/book/<int:flight_id>/', flights_views.booking_page, name='booking_page'),
    path('flights/', flights_views.flights, name='flights'),
    path('flight/<int:flight_id>/', flights_views.flight_details, name='flight_details'),
    path('manage-booking/', flights_views.manage_booking, name='manage-booking'),
    path('register/', flights_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('profile/edit/', flights_views.profile_edit, name='profile_edit'),
]

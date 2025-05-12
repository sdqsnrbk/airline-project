# flights/api_urls.py
from django.urls import path
from . import apiviews  # Import the API views we created

# Define a namespace for the API URLs if desired (optional but good practice)
# app_name = 'flights_api'

urlpatterns = [
    # /api/flights/ - List all flights
    path('flights/', apiviews.FlightListView.as_view(), name='api_flight_list'),

    # /api/flights/<id>/ - Get details for a specific flight
    # <int:pk> matches an integer and passes it as 'pk' (primary key) to the view
    path('flights/<int:pk>/', apiviews.FlightDetailView.as_view(), name='api_flight_detail'),

    # /api/bookings/ - Create a new booking (handles POST requests)
    path('bookings/', apiviews.BookingCreateView.as_view(), name='api_booking_create'),

    # /api/bookings/<booking_code>/ - Get details for a specific booking
    # <str:booking_code> matches a string and passes it as 'booking_code' to the view
    # This matches the 'lookup_url_kwarg' set in BookingDetailView
    path('bookings/<str:booking_code>/', apiviews.BookingDetailView.as_view(), name='api_booking_detail'),
]

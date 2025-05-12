# flights/apiviews.py
from rest_framework import generics, permissions
from .models import Flight, Booking, Airport # Import necessary models
from .serializers import ( # Import the serializers we created
    FlightSerializer,
    BookingListRetrieveSerializer,
    BookingCreateSerializer
)
from django.shortcuts import get_object_or_404

# --- Custom Permissions ---

class IsOwnerOrAdminReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to view it.
    Assumes the model instance has a `user` attribute.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to admins or the owner of the booking.
        if request.method in permissions.SAFE_METHODS: # SAFE_METHODS are GET, HEAD, OPTIONS
            return request.user.is_staff or obj.user == request.user
        # Write permissions are not allowed by this permission class (can be handled separately if needed)
        return False

# --- API Views ---

# 1. GET /api/flights/ - List all flights
class FlightListView(generics.ListAPIView):
    """
    API view to list all available flights.
    Accessible by any user (authenticated or not).
    """
    queryset = Flight.objects.select_related('origin', 'destination').all() # Optimized query
    serializer_class = FlightSerializer
    permission_classes = [permissions.AllowAny] # Anyone can view flights

# 2. GET /api/flights/<id>/ - Retrieve a specific flight
class FlightDetailView(generics.RetrieveAPIView):
    """
    API view to retrieve details of a specific flight by its ID.
    Accessible by any user.
    """
    queryset = Flight.objects.select_related('origin', 'destination').all()
    serializer_class = FlightSerializer
    permission_classes = [permissions.AllowAny] # Anyone can view flight details
    # The lookup field defaults to 'pk' (primary key, which is 'id' for Flight)

# 3. POST /api/bookings/ - Create a new booking
class BookingCreateView(generics.CreateAPIView):
    """
    API view to create a new booking.
    Requires authentication. Uses the logged-in user's details.
    """
    serializer_class = BookingCreateSerializer
    permission_classes = [permissions.IsAuthenticated] # Must be logged in to book via API

    # The serializer's create method handles associating the booking with request.user
    # We pass the request context to the serializer automatically via CreateAPIView

# 4. GET /api/bookings/<booking_code>/ - Retrieve a specific booking
class BookingDetailView(generics.RetrieveAPIView):
    """
    API view to retrieve details of a specific booking by its unique booking code.
    Requires the user to be the owner of the booking or an admin.
    """
    queryset = Booking.objects.select_related(
        'user', 'passenger', 'flight', 'flight__origin', 'flight__destination'
    ).all()
    serializer_class = BookingListRetrieveSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdminReadOnly] # Must be logged in AND owner/admin
    lookup_field = 'unique_booking_code' # Tell DRF to find the booking by this field instead of pk/id
    lookup_url_kwarg = 'booking_code' # The name of the argument in the URL pattern


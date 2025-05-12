# flights/serializers.py
from rest_framework import serializers
from .models import Airport, Flight, Passenger, Booking
from django.contrib.auth.models import User # Needed if you want to show user info in bookings

# --- Airport Serializer ---
class AirportSerializer(serializers.ModelSerializer):
    """
    Serializer for the Airport model.
    """
    class Meta:
        model = Airport
        fields = ['id', 'code', 'city'] # Fields to include in the JSON output

# --- Flight Serializer ---
class FlightSerializer(serializers.ModelSerializer):
    """
    Serializer for the Flight model.
    Uses nested serializers to show origin and destination airport details.
    """
    # Use the AirportSerializer to represent the origin and destination
    origin = AirportSerializer(read_only=True)
    destination = AirportSerializer(read_only=True)

    class Meta:
        model = Flight
        # Include relevant fields for flight listings and details
        fields = ['id', 'origin', 'destination', 'duration', 'capacity']
        # `read_only=True` on nested serializers means they won't be expected
        # when creating/updating flights via this serializer (if we were doing that).

# --- Passenger Serializer ---
class PassengerSerializer(serializers.ModelSerializer):
    """
    Serializer for the Passenger model.
    """
    class Meta:
        model = Passenger
        fields = ['id', 'name', 'email']

# --- User Serializer (Optional - for showing user details in booking) ---
class UserSerializer(serializers.ModelSerializer):
    """
    Basic serializer for the User model (read-only).
    Used to show who booked a flight.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = fields # Make all fields read-only


# --- Booking Serializer ---
class BookingListRetrieveSerializer(serializers.ModelSerializer):
    """
    Serializer for LISTING and RETRIEVING Bookings.
    Shows nested details for passenger and flight.
    Optionally shows user details.
    """
    # Use nested serializers for related objects
    passenger = PassengerSerializer(read_only=True)
    flight = FlightSerializer(read_only=True)
    user = UserSerializer(read_only=True) # Show basic user info

    class Meta:
        model = Booking
        fields = ['id', 'unique_booking_code', 'user', 'passenger', 'flight']


class BookingCreateSerializer(serializers.ModelSerializer):
    """
    Serializer specifically for CREATING Bookings via the API.
    Takes 'flight_id' as input.
    Handles associating the booking with the authenticated user.
    """
    # We expect a flight ID when creating a booking via the API
    # `write_only=True` means this field is used for input but not shown in output representation
    flight_id = serializers.IntegerField(write_only=True)

    # We don't include 'user' or 'passenger' here because they will be determined
    # by the view based on the authenticated user making the request.

    class Meta:
        model = Booking
        fields = ['flight_id'] # Only need flight_id for input via API for logged-in user

    def create(self, validated_data):
        """
        Custom create method to handle booking creation logic.
        Associates the booking with the authenticated user making the request.
        """
        # Get the authenticated user from the request context (passed by the view)
        user = self.context['request'].user
        if not user.is_authenticated:
             raise serializers.ValidationError("User must be authenticated to create a booking.")

        # Get flight object from the validated flight_id
        try:
            flight = Flight.objects.get(pk=validated_data['flight_id'])
        except Flight.DoesNotExist:
            raise serializers.ValidationError("Invalid flight_id.")

        # Check flight capacity (example validation - add more if needed)
        # Note: This is a simplified check; real-world would need atomic transactions
        # to prevent race conditions.
        current_bookings_count = Booking.objects.filter(flight=flight).count()
        if current_bookings_count >= flight.capacity:
             raise serializers.ValidationError("This flight is already full.")

        # Get or create the Passenger record based on the user's profile
        passenger_name = f"{user.first_name} {user.last_name}".strip()
        passenger_email = user.email
        if not passenger_name or not passenger_email:
            raise serializers.ValidationError("User profile is incomplete (missing name or email).")

        passenger, created = Passenger.objects.get_or_create(
            email=passenger_email,
            defaults={'name': passenger_name}
        )
        if not created and passenger.name != passenger_name:
            passenger.name = passenger_name
            passenger.save()

        # Create the booking instance
        booking = Booking.objects.create(
            user=user,
            passenger=passenger,
            flight=flight,
            # unique_booking_code is generated automatically by the model's save method
            **validated_data # Pass any other validated fields if they existed
        )
        return booking


# flights/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Flight, Booking, Passenger, Airport # Your existing model imports

# Imports for authentication and forms
from django.contrib.auth.decorators import login_required # Ensure this is imported
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .forms import UserRegisterForm, UserUpdateForm

# ... (index, flights, flight_details, airport views) ...
def index(request):
    return render(request, 'index.html')

def flights(request):
    flights_list = Flight.objects.all()
    return render(request, 'flights.html', {'flights': flights_list})

def flight_details(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    return render(request, 'flight_details.html', {'flight': flight})

def airport(request, airport_id):
    airport_obj = get_object_or_404(Airport, id=airport_id)
    arriving_flights = Flight.objects.filter(destination=airport_obj)
    departing_flights = Flight.objects.filter(origin=airport_obj)
    return render(request, 'airport.html', {
        'airport': airport_obj,
        'arriving_flights': arriving_flights,
        'departing_flights': departing_flights
    })


@login_required # Protects the booking page
def booking_page(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)

    if request.method == "POST":
        user = request.user
        passenger_name = f"{user.first_name} {user.last_name}".strip()
        passenger_email = user.email

        if not passenger_name or not passenger_email:
            messages.error(request, 'Your profile is incomplete (missing name or email). Please update your profile.')
            return redirect('profile_edit')

        passenger, created = Passenger.objects.get_or_create(
            email=passenger_email,
            defaults={'name': passenger_name}
        )
        if not created and passenger.name != passenger_name:
            passenger.name = passenger_name
            passenger.save()

        current_booking = Booking.objects.create(
            passenger=passenger,
            flight=flight,
            user=user
        )
        messages.success(request, f"Booking confirmed for {passenger_name}! Your booking code is {current_booking.unique_booking_code}.")
        return redirect('booking_confirmation', booking_code=current_booking.unique_booking_code)

    context = {
        'flight': flight,
        'user_full_name': f"{request.user.first_name} {request.user.last_name}".strip(),
        'user_email': request.user.email
    }
    return render(request, 'booking.html', context)

@login_required # Added protection
def booking_confirmation(request, booking_code):
    # Use select_related to fetch related user, passenger, flight, origin, destination in one query
    booking = get_object_or_404(
        Booking.objects.select_related(
            'user', 'passenger', 'flight', 'flight__origin', 'flight__destination'
        ),
        unique_booking_code=booking_code
    )
    # Ensure only the user who booked or an admin can see this
    if not request.user.is_staff and booking.user != request.user:
         messages.error(request, "You do not have permission to view this booking.")
         # Redirect to 'my_bookings' page once it exists, or index for now
         return redirect('index') # CHANGE LATER: redirect('manage_booking') would be better
    return render(request, 'confirmation.html', {'booking': booking})

@login_required
def manage_booking(request):
    """
    Handles displaying a list of the user's bookings (GET)
    and looking up a specific booking by code (POST).
    """
    user_bookings = None
    searched_booking = None
    search_attempted = False

    # Handle POST request (lookup specific booking code)
    if request.method == "POST":
        search_attempted = True # Flag that a search was done
        booking_code = request.POST.get('booking_code')
        if not booking_code:
            messages.error(request, "Please enter a booking code.")
            # Fetch user's bookings even if POST fails, to display the list
            user_bookings = Booking.objects.filter(user=request.user).select_related(
                'passenger', 'flight', 'flight__origin', 'flight__destination'
            ).order_by('-id') # Order by most recent first
            return render(request, 'manage_booking.html', {'user_bookings': user_bookings, 'searched': search_attempted})

        try:
            # Use select_related for efficiency
            booking = Booking.objects.select_related(
                'user', 'passenger', 'flight', 'flight__origin', 'flight__destination'
            ).get(unique_booking_code__iexact=booking_code)

            # Ensure only the user who booked or an admin can see this
            if not request.user.is_staff and booking.user != request.user:
                messages.error(request, "You do not have permission to view this booking code.")
            else:
                # Booking found and authorized
                searched_booking = booking
        except Booking.DoesNotExist:
            messages.error(request, "Invalid booking code.")

        # If search failed or unauthorized, searched_booking remains None
        if not searched_booking:
             messages.info(request, f"Could not find details for booking code: {booking_code}")

    # For both GET requests and after POST requests, fetch the list of user's bookings
    user_bookings = Booking.objects.filter(user=request.user).select_related(
        'passenger', 'flight', 'flight__origin', 'flight__destination'
    ).order_by('-id') # Order by most recent first

    context = {
        'user_bookings': user_bookings,
        'searched_booking': searched_booking, # Result of the POST search (if any)
        'searched': search_attempted # Flag to indicate if a search was performed via POST
    }
    return render(request, 'manage_booking.html', context)


# ... (register view) ...
def register(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect('index')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegisterForm() # Corrected: Was missing ()
    return render(request, 'register.html', {'form': form, 'title': 'Register'})

# ... (profile_edit view) ...
@login_required
def profile_edit(request):
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            profile_form = UserUpdateForm(request.POST, instance=request.user)
            password_form = PasswordChangeForm(request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Your profile has been updated successfully!')
                return redirect('profile_edit')
            else:
                messages.error(request, 'Please correct the profile errors below.')
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            profile_form = UserUpdateForm(instance=request.user)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password was successfully updated!')
                return redirect('profile_edit')
            else:
                messages.error(request, 'Please correct the password errors below.')
        else:
            profile_form = UserUpdateForm(instance=request.user)
            password_form = PasswordChangeForm(request.user)
            messages.error(request, 'Invalid form submission. Please try again.')
    else:
        profile_form = UserUpdateForm(instance=request.user)
        password_form = PasswordChangeForm(request.user)

    context = {
        'title': 'Edit Account',
        'profile_form': profile_form,
        'password_form': password_form
    }
    return render(request, 'profile_edit.html', context)

# flights/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Flight, Booking, Passenger, Airport # Your existing model imports

# Imports for authentication and forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .forms import UserRegisterForm, UserUpdateForm # UserUpdateForm is for profile_edit

def index(request):
    return render(request, 'index.html')

def flights(request):
    flights_list = Flight.objects.all() # Renamed to avoid conflict with the function name
    return render(request, 'flights.html', {'flights': flights_list})

def flight_details(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    return render(request, 'flight_details.html', {'flight': flight})

def airport(request, airport_id):
    airport_obj = get_object_or_404(Airport, id=airport_id) # Renamed to avoid conflict
    arriving_flights = Flight.objects.filter(destination=airport_obj)
    departing_flights = Flight.objects.filter(origin=airport_obj)
    return render(request, 'airport.html', {
        'airport': airport_obj,
        'arriving_flights': arriving_flights,
        'departing_flights': departing_flights
    })

def booking_page(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)

    # NOTE: This view will need to be updated in Phase 2 to handle authenticated users
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')

        if not name or not email:
            messages.error(request, 'Name and email are required!') # Using messages framework
            return render(request, 'booking.html', {'flight': flight})

        # This passenger creation logic will change.
        # For now, it creates a new Passenger object for each booking.
        # Later, if a user is logged in, we'll link to their User object.
        passenger, created = Passenger.objects.get_or_create(
            email=email, defaults={'name': name}
        )
        if not created and passenger.name != name: # If email exists with different name, update name or handle as error
            passenger.name = name # Or decide on a different strategy
            passenger.save()


        booking = Booking.objects.create(
            passenger=passenger,
            flight=flight
            # user=request.user if request.user.is_authenticated else None # This will be added later
        )
        messages.success(request, f"Booking confirmed! Your booking code is {booking.unique_booking_code}.")
        return redirect('booking_confirmation', booking_code=booking.unique_booking_code)

    return render(request, 'booking.html', {'flight': flight})

def booking_confirmation(request, booking_code):
    booking = get_object_or_404(Booking, unique_booking_code=booking_code)
    return render(request, 'confirmation.html', {'booking': booking})

def manage_booking(request):
    # This view might also need updates based on user authentication later
    if request.method == "POST":
        booking_code = request.POST.get('booking_code')
        if not booking_code: # Basic validation
            messages.error(request, "Please enter a booking code.")
            return redirect('manage_booking')

        try:
            booking = Booking.objects.get(unique_booking_code__iexact=booking_code) # Case-insensitive lookup
            # Add logic here to check if the logged-in user is allowed to see this booking
        except Booking.DoesNotExist:
            booking = None

        if not booking:
            messages.error(request, "Invalid booking code.")
            return redirect('manage_booking') # Redirect back to the form

        return render(request, 'manage_booking.html', {'booking': booking, 'searched': True})

    return render(request, 'manage_booking.html', {'searched': False})

def register(request):
    """
    Handles user registration.
    """
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
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form, 'title': 'Register'})

@login_required # Ensures only logged-in users can access this view
def profile_edit(request):
    """
    Handles displaying and processing forms for a user to edit their profile
    (email) and change their password. Username, first name, last name are read-only.
    """
    if request.method == 'POST':
        # Check which form was submitted based on the button's name attribute
        if 'update_profile' in request.POST:
            profile_form = UserUpdateForm(request.POST, instance=request.user)
            # Initialize password_form to display it correctly even if profile_form is invalid
            password_form = PasswordChangeForm(request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Your profile has been updated successfully!')
                return redirect('profile_edit') # Redirect to the same page
            else:
                messages.error(request, 'Please correct the profile errors below.')
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            # Initialize profile_form to display it correctly if password_form is invalid
            profile_form = UserUpdateForm(instance=request.user)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Important! Keeps the user logged in.
                messages.success(request, 'Your password was successfully updated!')
                return redirect('profile_edit') # Redirect to the same page
            else:
                messages.error(request, 'Please correct the password errors below.')
        else:
            # This case should ideally not be reached if buttons have proper names
            profile_form = UserUpdateForm(instance=request.user)
            password_form = PasswordChangeForm(request.user)
            messages.error(request, 'Invalid form submission. Please try again.')
    else: # GET request
        profile_form = UserUpdateForm(instance=request.user)
        password_form = PasswordChangeForm(request.user)

    context = {
        'title': 'Edit Account',
        'profile_form': profile_form,
        'password_form': password_form
    }
    return render(request, 'profile_edit.html', context)

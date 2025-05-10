from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Flight, Booking, Passenger, Airport

def index(request):
    return render(request, 'index.html')

def flights(request):
    flights = Flight.objects.all()
    return render(request, 'flights.html', {'flights': flights})

def flight_details(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    return render(request, 'flight_details.html', {'flight': flight})

def airport(request, airport_id):
    airport = get_object_or_404(Airport, id=airport_id)
    arriving_flights = Flight.objects.filter(destination=airport)
    departing_flights = Flight.objects.filter(origin=airport)
    return render(request, 'airport.html', {
        'airport': airport,
        'arriving_flights': arriving_flights,
        'departing_flights': departing_flights
    })

def booking_page(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)

    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')

        if not name or not email:
            return render(request, 'booking.html', {'flight': flight, 'error': 'Name and email are required!'})

        passenger = Passenger.objects.create(name=name, email=email)

        booking = Booking.objects.create(
            passenger=passenger,
            flight=flight
        )

        return redirect('booking_confirmation', booking_code=booking.unique_booking_code)

    return render(request, 'booking.html', {'flight': flight})

def booking_confirmation(request, booking_code):
    booking = get_object_or_404(Booking, unique_booking_code=booking_code)
    return render(request, 'confirmation.html', {'booking': booking})

def manage_booking(request):
    if request.method == "POST":
        booking_code = request.POST.get('booking_code')

        booking = Booking.objects.filter(unique_booking_code=booking_code).first()
        if not booking:
            messages.error(request, "Invalid booking code.")
            return redirect('manage_booking')

        return render(request, 'manage_booking.html', {'booking': booking})

    return render(request, 'manage_booking.html')

from django.db import models
import uuid
import string
import random

class Airport(models.Model):
    code = models.CharField(max_length=3, unique=True)
    city = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.city} ({self.code})"

class Flight(models.Model):
    origin = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='flights_from')
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='flights_to')
    duration = models.IntegerField()
    capacity = models.IntegerField()

    def __str__(self):
        return f"{self.origin} to {self.destination}"

class Passenger(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name


class Booking(models.Model):
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    unique_booking_code = models.CharField(max_length=6, unique=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.unique_booking_code:
            self.unique_booking_code = self.generate_unique_booking_code()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_unique_booking_code():
        characters = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(random.choice(characters) for _ in range(6))
            if not Booking.objects.filter(unique_booking_code=code).exists():
                return code

    def __str__(self):
        return f"Booking for {self.passenger.name} - {self.unique_booking_code}"
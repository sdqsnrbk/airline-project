from django.contrib import admin
from django.urls import include, path
from flights import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.index, name="index"),
    path('index/', views.index, name='index'),
    path('flights/airport/<int:airport_id>/', views.airport, name='airport_details'),
    path('booking/confirmation/<str:booking_code>/', views.booking_confirmation, name='booking_confirmation'),
    path('flights/book/<int:flight_id>/', views.booking_page, name='booking_page'),
    path('flights/', views.flights, name='flights'),
    path('flight/<int:flight_id>/', views.flight_details, name='flight_details'),
    path('manage-booking/', views.manage_booking, name='manage-booking'),
]
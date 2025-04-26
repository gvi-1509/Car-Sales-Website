from django.db import models
from django.utils import timezone
from django.conf import settings
from datetime import datetime

class Car(models.Model):
    DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'  # Explicitly set primary key type

    FUEL_TYPE_CHOICES = [
        ('lpg', 'LPG'),
        ('cng', 'CNG'),
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
    ]
    TRANSMISSION_TYPE_CHOICES = [
        ('automatic', 'Automatic'),
        ('manual', 'Manual'),
    ]
    CAR_OWNER_CHOICES = [
        ('first owner', 'First Owner'),
        ('second owner', 'Second Owner'),
        ('third owner', 'Third Owner'),
        ('fourth owner or more', 'Fourth Owner or More'),
    ]
    INSURANCE_TYPE_CHOICES = [
        ('comprehensive', 'Comprehensive'),
        ('third party', 'Third Party'),
        ('expired', 'Expired'),
    ]
    REGISTRATION_TYPE_CHOICES = [
        ('individual', 'Individual'),
        ('corporate', 'Corporate'),
        ('taxi', 'Taxi'),
    ]
    CAR_STATUS_OPTIONS = [
        ('active', 'Active'),
        ('deactive', 'Deactive'),
    ]
    VEHICLE_TYPE_CHOICES = [
        ('Car', 'Car'),
        ('Bike', 'Bike'),
        ('Truck', 'Truck'),
        ('Tractor', 'Tractor'),
        ('Auto Rickshaw', 'Auto Rickshaw'),
        ('Agriculture Instrument', 'Agriculture Instrument'),
    ]
    CITY_CHOICES = [
        ('Patna', 'Patna'),
        ('Ranchi', 'Ranchi'),
        ('Dhanbad', 'Dhanbad'),
        ('Gaya', 'Gaya'),
        ('Other', 'Other'),
    ]

    id = models.BigAutoField(primary_key=True)  # Explicit primary key
    car_title = models.CharField(max_length=100)
    make_year = models.IntegerField()
    make_month = models.CharField(max_length=100, blank=True, null=True)
    car_manufacturer = models.CharField(max_length=100)
    car_model = models.CharField(max_length=100)
    car_version = models.CharField(max_length=100, blank=True, null=True)
    car_color = models.CharField(max_length=100, blank=True, null=True)
    fuel_type = models.CharField(max_length=25, choices=FUEL_TYPE_CHOICES, default='petrol')
    transmission_type = models.CharField(max_length=25, choices=TRANSMISSION_TYPE_CHOICES, default='manual')
    car_owner = models.CharField(max_length=25, choices=CAR_OWNER_CHOICES, default='first owner')
    kilometer_driven = models.IntegerField(blank=True, null=True)
    expected_selling_price = models.IntegerField()
    registration_type = models.CharField(max_length=25, choices=REGISTRATION_TYPE_CHOICES, default='individual')
    insurance_type = models.CharField(max_length=25, choices=INSURANCE_TYPE_CHOICES, default='expired')
    registration_number = models.CharField(max_length=30, blank=True, null=True)
    car_description = models.TextField(blank=True, null=True)
    car_post_date = models.DateField(default=datetime.now)
    car_photo = models.ImageField(upload_to='car/car_images/', blank=True, null=True)
    car_status = models.CharField(max_length=25, choices=CAR_STATUS_OPTIONS, default='active')
    vehicle_type = models.CharField(max_length=25, choices=VEHICLE_TYPE_CHOICES, default='Car')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Link to User model
    car_owner_phone_number = models.CharField(max_length=15, default="", blank=True, null=True)  # Store phone as string
    car_city = models.CharField(max_length=50, choices=CITY_CHOICES, default='Patna')
    car_owner_name = models.CharField(max_length=100, default="-")

    class Meta:
        ordering = ('car_title',)

    def __str__(self):
        return self.car_title


class Privacy(models.Model):
    id = models.BigAutoField(primary_key=True)  # Explicit primary key
    privacy_policy = models.TextField()

    class Meta:
        verbose_name_plural = "Privacy"

    def __str__(self):
        return self.privacy_policy


class Ads(models.Model):
    id = models.BigAutoField(primary_key=True)  # Explicit primary key
    popup_ad = models.ImageField(upload_to='car/car_images/', blank=True, null=True)
    popup_ad_url = models.URLField(max_length=400, blank=True, null=True)
    ad1 = models.ImageField(upload_to='car/car_images/', blank=True, null=True)
    ad1_url = models.URLField(max_length=400, blank=True, null=True)
    ad2 = models.ImageField(upload_to='car/car_images/', blank=True, null=True)
    ad2_url = models.URLField(max_length=400, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Ads"

    def __str__(self):
        return str(self.popup_ad)


class Client(models.Model):
    id = models.BigAutoField(primary_key=True)  # Explicit primary key
    name = models.CharField(max_length=100, default="-", blank=True, null=True)
    phone_number = models.CharField(max_length=15, default="")  # Store phone as string

    class Meta:
        verbose_name_plural = "Client Phone Number"

    def __str__(self):
        return str(self.name)

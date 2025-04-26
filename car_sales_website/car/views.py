import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden, HttpResponseRedirect
from django.core.management import call_command
from django.db.models import Q
from django_ratelimit.decorators import ratelimit

from .models import Car, Client, Privacy, Ads

# Helper function

def redirect_with_anchor(request, anchor):
    return redirect(f"{request.META['HTTP_REFERER']}#{anchor}")

# Home page
def index(request):
    allcars = Car.objects.filter(vehicle_type="Car")
    total_vehicles = allcars.count()
    context = {'allcars': allcars, 'total_vehicles': total_vehicles}
    return render(request, 'index-3.html', context)

# Listing classic cars
def listing_classic(request):
    allcars = Car.objects.all()
    paginator = Paginator(allcars, 8)
    page_number = request.GET.get('page')
    allcars = paginator.get_page(page_number)
    total_vehicles = Car.objects.count()
    context = {'allcars': allcars, 'total_vehicles': total_vehicles}
    return render(request, 'listing-classic.html', context)

# Car detail page
def listing_detail(request, myid):
    car = get_object_or_404(Car, id=myid)
    otp_verified = request.session.get('otp_verified', False)
    context = {'car': car, 'otp_verified': otp_verified}
    return render(request, 'listing-detail.html', context)

# Search cars
def search(request):
    if request.method == 'GET':
        car_city = request.GET.get('city')
        vehicle_type = request.GET.get('vehicle_type')
        slider_range = request.GET.get('slider', "0,10000000").split(",")
        min_price, max_price = map(int, slider_range)

        filters = Q(expected_selling_price__range=(min_price, max_price))

        if car_city != "Select Location":
            filters &= Q(car_city=car_city)

        if vehicle_type != "Select Vehicle Type":
            filters &= Q(vehicle_type=vehicle_type)

        result = Car.objects.filter(filters)
        total_vehicles = result.count()
        context = {'result': result, 'allcars': Car.objects.all(), 'total_vehicles': total_vehicles}
        return render(request, 'search.html', context)

# Sort all cars
def sort(request):
    if request.method == 'GET':
        sort = request.GET.get('sort')
        sorted = Car.objects.all()
        low_to_high = None

        if sort == "Price (low to high)":
            sorted = sorted.order_by("expected_selling_price")
            low_to_high = True
        elif sort == "Price (high to low)":
            sorted = sorted.order_by("-expected_selling_price")
            low_to_high = False

        context = {'sorted': sorted, 'allcars': Car.objects.all(), 'total_vehicles': sorted.count(), 'low_to_high': low_to_high}
        return render(request, 'sort.html', context)

# Post a vehicle
@login_required(login_url='/#loginModal')
def post_vehicle(request):
    if request.method == 'POST':
        data = request.POST
        try:
            car = Car(
                car_title=data['car_title'],
                make_year=int(data['make_year']) if data['make_year'].isdigit() else None,
                make_month=data['make_month'],
                car_manufacturer=data['car_manufacturer'],
                car_model=data['car_model'],
                car_version=data['car_version'],
                car_color=data['car_color'],
                fuel_type=data['fuel_type'],
                transmission_type=data['transmission_type'],
                car_owner=data['car_owner'],
                kilometer_driven=int(data['kilometer_driven']) if data['kilometer_driven'].isdigit() else None,
                expected_selling_price=int(data['expected_selling_price']) if data['expected_selling_price'].isdigit() else None,
                registration_type=data['registration_type'],
                insurance_type=data['insurance_type'],
                registration_number=data['registration_number'],
                car_description=data['car_description'],
                car_photo=request.FILES['car_photo'],
                car_owner_phone_number=int(data['car_owner_phone_number']) if data['car_owner_phone_number'].isdigit() else None,
                car_city=data['car_city'],
                car_owner_name=data['car_owner_name'],
                user=request.user,
            )
            car.save()
            return redirect('my_vehicles')
        except Exception as e:
            messages.error(request, f"Error saving vehicle: {str(e)}")

    return render(request, 'post-vehicle.html', {})

# Display user's vehicles
@login_required(login_url='/#loginModal')
def my_vehicles(request):
    cars = Car.objects.filter(user=request.user)
    return render(request, 'my-vehicles.html', {'cars': cars})

# Delete vehicle
@login_required(login_url='/#loginModal')
def delete_vehicles(request, myid):
    obj = get_object_or_404(Car, id=myid)
    if obj.user != request.user:
        return HttpResponseForbidden("You are not allowed to delete this vehicle.")

    try:
        call_command('dbbackup')
    except Exception:
        pass

    if request.method == "POST":
        obj.delete()
        return redirect('my-vehicles')

    return render(request, 'my-vehicles.html', {})

# Profile settings
@login_required(login_url='/#loginModal')
def profile_settings(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect(request.META['HTTP_REFERER'])
        else:
            messages.error(request, 'Please retry for password change')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'profile-settings.html', {'form': form})

# About us page
def about_us(request):
    return render(request, 'about-us.html')

# Signup
@ratelimit(key='ip', rate='10/h', block=True)
def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if len(username) > 15:
            messages.error(request, "Username must be under 15 characters")
            return redirect_with_anchor(request, "signupModal")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect_with_anchor(request, "signupModal")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect_with_anchor(request, "signupModal")

        if pass1 != pass2:
            messages.error(request, "Passwords do not match")
            return redirect_with_anchor(request, "signupModal")

        if len(pass1) < 6:
            messages.error(request, "Password must be at least 6 characters")
            return redirect_with_anchor(request, "signupModal")

        myuser = User.objects.create_user(username, email, pass1)
        myuser.save()
        user = authenticate(username=username, password=pass1)
        if user is not None:
            login(request, user)
            messages.success(request, "Successfully Logged In")
        return redirect(request.META['HTTP_REFERER'])

    return HttpResponse('404 - Not Found')

# Login
@ratelimit(key='ip', rate='10/h', block=True)
def login_model(request):
    if request.method == 'POST':
        username = request.POST['loginusername']
        password = request.POST['loginpass']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Successfully Logged In")
            return redirect(request.META['HTTP_REFERER'])
        else:
            messages.error(request, "Invalid Credentials")
            return redirect_with_anchor(request, "loginModal")
    return HttpResponse("404 - Not Found")

# Logout
def logout_model(request):
    logout(request)
    messages.success(request, "Successfully Logged Out")
    return redirect(request.META['HTTP_REFERER'])

# Privacy page
def privacy(request):
    policy = Privacy.objects.first()
    return render(request, 'privacy.html', {'policy': policy})

# Submit phone number
@ratelimit(key='ip', rate='10/h', block=True)
def submit_number(request):
    if request.method == 'POST':
        ph_number = int(request.POST['phone_number'])
        request.session['session_phone_number'] = ph_number
        request.session['session_phone_name'] = request.POST['phone_name']
        request.session['session_otp_car_id'] = request.POST['car_id']

        if Client.objects.filter(phone_number=ph_number).exists():
            request.session['otp_verified'] = True
            return redirect(f"listing-detail.html/{request.session['session_otp_car_id']}")
        else:
            request.session['session_otp'] = random.randint(1000, 9999)
            return redirect(f"listing-detail.html/{request.session['session_otp_car_id']}#submit_otp")
    return HttpResponse("404 - Not Found")

# Submit OTP
def submit_otp(request):
    if request.method == 'POST':
        get_otp = request.POST['get_otp']
        if int(get_otp) == int(request.session.get('session_otp', 0)):
            Client.objects.create(name=request.session['session_phone_name'], phone_number=request.session['session_phone_number'])
            request.session['otp_verified'] = True
            return redirect(f"listing-detail.html/{request.session['session_otp_car_id']}")
        else:
            return redirect(f"listing-detail.html/{request.session['session_otp_car_id']}#submit_otp")
    return HttpResponse("404 - Details Not Found")

# Disclaimer page
def disclaimer(request):
    return render(request, 'Disclaimer.html')

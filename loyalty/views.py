import random
import qrcode
import io
import base64
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Customer, Transaction

def phone_entry_view(request):
    if request.method == 'POST':
        phone = request.POST.get('phone_number')
        if phone:
            otp = str(random.randint(1000, 9999))
            request.session['otp'] = otp
            request.session['temp_phone'] = phone
            print(f"=== OTP for {phone} is {otp} ===")
            return redirect('verify_otp')
    return render(request, 'loyalty/phone_entry.html')

def verify_otp_view(request):
    session_otp = request.session.get('otp')
    phone = request.session.get('temp_phone')
    
    if not phone:
        return redirect('phone_entry')

    if request.method == 'POST':
        user_otp = request.POST.get('otp')
        if user_otp == session_otp:
            customer, created = Customer.objects.get_or_create(phone_number=phone)
            request.session['authenticated_customer_id'] = customer.id
            if created or not customer.has_usable_password():
                return redirect('set_password')
            else:
                login(request, customer)
                return redirect('dashboard')
        else:
            messages.error(request, "Invalid code. Please try again.")

    return render(request, 'loyalty/verify_otp.html', {'phone': phone, 'demo_otp': session_otp})

def set_password_view(request):
    customer_id = request.session.get('authenticated_customer_id')
    if not customer_id:
        return redirect('phone_entry')

    customer = Customer.objects.get(id=customer_id)

    if request.method == 'POST':
        password = request.POST.get('password')
        if password and len(password) >= 6:
            customer.set_password(password)
            customer.save()
            login(request, customer)
            return redirect('dashboard')
        else:
            messages.error(request, "Password must be at least 6 characters.")

    return render(request, 'loyalty/set_password.html')

@login_required
def dashboard_view(request):
    customer = request.user
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(str(customer.qr_code_id))
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_b64 = base64.b64encode(buffer.getvalue()).decode()
    transactions = customer.transactions.all().order_by('-created_at')

    return render(request, 'loyalty/dashboard.html', {
        'customer': customer,
        'qr_b64': qr_b64,
        'transactions': transactions
    })

@user_passes_test(lambda u: u.is_staff)
def add_points_staff_view(request, qr_id):
    customer = get_object_or_404(Customer, qr_code_id=qr_id)
    if request.method == 'POST':
        amount = float(request.POST.get('amount_spent', 0))
        points = int(amount // 10)
        customer.points += points
        customer.save()
        Transaction.objects.create(
            customer=customer,
            amount_spent=amount,
            points_added=points,
            description=f"Spent {amount:.2f} AED"
        )
        messages.success(request, f"Added {points} points to {customer.phone_number}")
        return redirect('admin:index')
    return render(request, 'loyalty/staff_add_points.html', {'customer': customer})

def logout_view(request):
    logout(request)
    return redirect('phone_entry')
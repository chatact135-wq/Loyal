from django.urls import path
from . import views

urlpatterns = [
    path('', views.phone_entry_view, name='phone_entry'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('set-password/', views.set_password_view, name='set_password'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('staff/add-points/<uuid:qr_id>/', views.add_points_staff_view, name='staff_add_points'),
    path('logout/', views.logout_view, name='logout'),
]
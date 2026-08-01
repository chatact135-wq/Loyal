import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class CustomerManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('The Phone Number must be set')
        user = self.model(phone_number=phone_number, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone_number, password, **extra_fields)

class Customer(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=20, unique=True)
    points = models.IntegerField(default=7000)
    qr_code_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomerManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.phone_number} ({self.points} Points)"

class Transaction(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='transactions')
    amount_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    points_added = models.IntegerField(default=0)
    description = models.CharField(max_length=255, default="Purchase Reward")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.phone_number} - {self.points_added} pts on {self.created_at.strftime('%Y-%m-%d')}"

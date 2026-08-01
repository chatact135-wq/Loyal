from django.contrib import admin
from .models import Customer, Transaction

@admin.action(description='Gift 100 Points to selected customers')
def gift_100_points(modeladmin, request, queryset):
    for customer in queryset:
        customer.points += 100
        customer.save()
        Transaction.objects.create(customer=customer, points_added=100, description="Manual Gift: 100 Points")

@admin.action(description='Gift 500 Points to selected customers')
def gift_500_points(modeladmin, request, queryset):
    for customer in queryset:
        customer.points += 500
        customer.save()
        Transaction.objects.create(customer=customer, points_added=500, description="Manual Gift: 500 Points")

class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0
    readonly_fields = ('created_at',)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'points', 'qr_code_id', 'date_joined')
    search_fields = ('phone_number',)
    actions = [gift_100_points, gift_500_points]
    inlines = [TransactionInline]

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('customer', 'amount_spent', 'points_added', 'description', 'created_at')
    list_filter = ('created_at',)

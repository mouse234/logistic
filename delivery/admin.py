from django.contrib import admin
from .models import Customer, Address, Order, OrderItem, Driver, DeliveryUpdate


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


class DeliveryUpdateInline(admin.TabularInline):
    model = DeliveryUpdate
    extra = 0
    readonly_fields = ('timestamp',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'status', 'assigned_driver', 'created_at')
    list_filter = ('status', 'created_at')
    inlines = [OrderItemInline, DeliveryUpdateInline]
    actions = ['mark_delivered']

    def mark_delivered(self, request, queryset):
        updated = queryset.update(status='DELIVERED')
        self.message_user(request, f"{updated} orders marked as delivered")
    mark_delivered.short_description = 'Mark selected orders as Delivered'


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('customer', 'street', 'city', 'state', 'pincode')
    list_filter = ('city', 'state')
    search_fields = ('street', 'city')


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'vehicle_number', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'vehicle_number')


@admin.register(DeliveryUpdate)
class DeliveryUpdateAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'location', 'timestamp')
    list_filter = ('status', 'timestamp')
    readonly_fields = ('timestamp',)

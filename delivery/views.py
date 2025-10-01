from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.forms import formset_factory
from django.views.decorators.http import require_POST
from .models import Order, Customer, Address, OrderItem, DeliveryUpdate, Driver
from .forms import AddressForm, OrderCreateForm, OrderItemForm


def home(request):
    """Home page with basic information"""
    return render(request, 'delivery/home.html')


@login_required
def dashboard(request):
    """Admin dashboard for staff to manage orders"""
    if not request.user.is_staff:
        return redirect('order_list')
    
    orders = Order.objects.all().order_by('-created_at')[:50]
    drivers = Driver.objects.filter(is_active=True)
    
    # Statistics
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='PENDING').count()
    in_transit_orders = Order.objects.filter(status='IN_TRANSIT').count()
    delivered_orders = Order.objects.filter(status='DELIVERED').count()
    
    context = {
        'orders': orders,
        'drivers': drivers,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'in_transit_orders': in_transit_orders,
        'delivered_orders': delivered_orders,
    }
    return render(request, 'delivery/admin/dashboard.html', context)


@login_required
def order_create(request):
    """Customer places an order"""
    user = request.user
    customer, _ = Customer.objects.get_or_create(user=user, defaults={'phone': ''})

    OrderItemFormSet = formset_factory(OrderItemForm, extra=1, min_num=1)

    if request.method == 'POST':
        pickup_form = AddressForm(request.POST, prefix='pickup')
        delivery_form = AddressForm(request.POST, prefix='delivery')
        order_form = OrderCreateForm(request.POST)
        items_formset = OrderItemFormSet(request.POST, prefix='items')

        if pickup_form.is_valid() and delivery_form.is_valid() and order_form.is_valid() and items_formset.is_valid():
            # Save addresses
            pickup = pickup_form.save(commit=False)
            pickup.customer = customer
            pickup.save()
            
            delivery = delivery_form.save(commit=False)
            delivery.customer = customer
            delivery.save()

            # Save order
            order = order_form.save(commit=False)
            order.customer = customer
            order.pickup_address = pickup
            order.delivery_address = delivery
            order.save()

            # Save order items
            for item_form in items_formset:
                if item_form.cleaned_data and item_form.cleaned_data.get('name'):
                    item = item_form.save(commit=False)
                    item.order = order
                    item.save()

            # Create initial delivery update
            DeliveryUpdate.objects.create(
                order=order, 
                status='PENDING', 
                note='Order created and awaiting assignment'
            )
            
            messages.success(request, f'Order #{order.id} created successfully!')
            return redirect('order_detail', order_id=order.id)
    else:
        pickup_form = AddressForm(prefix='pickup')
        delivery_form = AddressForm(prefix='delivery')
        order_form = OrderCreateForm()
        items_formset = OrderItemFormSet(prefix='items')

    context = {
        'pickup_form': pickup_form,
        'delivery_form': delivery_form,
        'order_form': order_form,
        'items_formset': items_formset,
    }
    return render(request, 'delivery/customer/order_create.html', context)


@login_required
def order_list(request):
    """List orders based on user role"""
    user = request.user
    
    if user.is_staff:
        orders = Order.objects.all().order_by('-created_at')
        template = 'delivery/admin/order_list.html'
    else:
        customer = Customer.objects.filter(user=user).first()
        orders = Order.objects.filter(customer=customer).order_by('-created_at') if customer else []
        template = 'delivery/customer/order_list.html'
    
    return render(request, template, {'orders': orders})


@login_required
def order_detail(request, order_id):
    """Show order details and tracking updates"""
    order = get_object_or_404(Order, id=order_id)
    
    # Check permissions - staff can see all orders, customers only their own
    if not request.user.is_staff:
        customer = Customer.objects.filter(user=request.user).first()
        if not customer or order.customer != customer:
            messages.error(request, "You don't have permission to view this order.")
            return redirect('order_list')
    
    updates = order.updates.all()
    items = order.items.all()
    
    context = {
        'order': order,
        'updates': updates,
        'items': items,
    }
    
    template = 'delivery/admin/order_detail.html' if request.user.is_staff else 'delivery/customer/order_detail.html'
    return render(request, template, context)


@require_POST
@login_required
def assign_driver(request, order_id):
    """Admin function to assign driver to order"""
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('order_list')
    
    order = get_object_or_404(Order, id=order_id)
    driver_id = request.POST.get('driver_id')
    
    if driver_id:
        driver = get_object_or_404(Driver, id=driver_id)
        order.assigned_driver = driver
        order.status = 'ASSIGNED'
        order.save()
        
        DeliveryUpdate.objects.create(
            order=order, 
            status='ASSIGNED', 
            note=f'Driver {driver.name} assigned to this order'
        )
        
        messages.success(request, f'Driver {driver.name} assigned to Order #{order.id}')
    
    return redirect('dashboard')


@require_POST
@login_required
def update_status(request, order_id):
    """Admin function to update order status"""
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('order_list')
    
    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get('status')
    note = request.POST.get('note', '')
    location = request.POST.get('location', '')
    
    # Valid status choices
    valid_statuses = [choice[0] for choice in Order._meta.get_field('status').choices]
    
    if new_status and new_status in valid_statuses:
        order.status = new_status
        order.save()
        
        DeliveryUpdate.objects.create(
            order=order, 
            status=new_status, 
            note=note,
            location=location
        )
        
        messages.success(request, f'Order #{order.id} status updated to {new_status}')
    else:
        messages.error(request, 'Invalid status selected')
    
    return redirect('dashboard')


def register(request):
    """User registration"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create customer profile
            Customer.objects.create(user=user, phone='')
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

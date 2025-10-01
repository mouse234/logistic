# Swift Nationwide Delivery — Django + SQL Server

**Project:** Swift Nationwide Delivery (Logistics Management System)

**Stack:** Django (Python), SQL Server (SSMS) via `mssql-django`, HTML templates, Bootstrap (optional)

**What this package contains:**
- Complete project structure and key code files (models, views, forms, templates, admin).
- Instructions to setup local development environment, install dependencies, configure SQL Server (SSMS) and Django connection.
- Customer-facing features: place order, view orders, track delivery.
- Admin-facing features: view/manage orders, assign driver, update delivery status, track vehicles.

> Note: This document includes full files and step-by-step commands. Copy each file into the corresponding file path in your Django project.

---

## Project structure (recommended)

```
swift_delivery/                # Django project root
├─ manage.py
├─ swift_delivery/             # Django project settings
│  ├─ __init__.py
│  ├─ settings.py
│  ├─ urls.py
│  └─ wsgi.py
├─ delivery/                    # main app
│  ├─ migrations/
│  ├─ templates/
│  │  ├─ base.html
│  │  ├─ customer/
│  │  │  ├─ order_create.html
│  │  │  ├─ order_list.html
│  │  │  └─ order_detail.html
│  │  └─ admin/
│  │     └─ dashboard.html
│  ├─ static/
│  ├─ __init__.py
│  ├─ admin.py
│  ├─ apps.py
│  ├─ forms.py
│  ├─ models.py
│  ├─ urls.py
│  └─ views.py
├─ requirements.txt
└─ README.md
```

---

## requirements.txt

```
Django>=4.2
mssql-django>=1.1.0
pyodbc>=4.0.0
django-crispy-forms
```

(Adjust versions as needed.)

---

## 1) Setup instructions (Windows + SSMS) — step-by-step

1. Install Python 3.10+ and add to PATH.
2. Install SQL Server (Express or Developer) and SSMS. Create a database named `swift_delivery_db`.
3. Install ODBC Driver for SQL Server (Microsoft ODBC Driver 18 for SQL Server). Download from Microsoft.
4. Create a virtual environment and install dependencies:

```bash
python -m venv venv
venv\Scripts\activate    # Windows
# or `source venv/bin/activate` on mac/linux
pip install --upgrade pip
pip install -r requirements.txt
```

5. Create the Django project and app (if not already):

```bash
django-admin startproject swift_delivery .
python manage.py startapp delivery
```

6. Configure database in `swift_delivery/settings.py` (see file snippet below). Make sure to replace username, password, and host.

7. Run migrations and create superuser:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

8. Start development server:

```bash
python manage.py runserver
```

9. Open browser: http://127.0.0.1:8000/ to view app. SSMS can be used to view database tables and rows.

---

## 2) Database configuration (settings.py)

Replace your `DATABASES` in `swift_delivery/settings.py` with:

```python
# settings.py (excerpt)
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'swift_delivery_db',
        'USER': 'your_sql_username',
        'PASSWORD': 'your_sql_password',
        'HOST': 'localhost',
        'PORT': '',
        'OPTIONS': {
            'driver': 'ODBC Driver 18 for SQL Server',
            # 'extra_params': 'Encrypt=yes;TrustServerCertificate=yes' # if needed
        },
    }
}
```

Also add `'delivery'` to `INSTALLED_APPS` and other required settings:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'delivery',
    'crispy_forms',
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'

STATIC_URL = '/static/'
STATICFILES_DIRS = [ BASE_DIR / 'delivery' / 'static' ]

LOGIN_REDIRECT_URL = '/'  # adjust
```

---

## 3) Models (`delivery/models.py`)

```python
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Address(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=20)
    def __str__(self):
        return f"{self.street}, {self.city}"

ORDER_STATUS = (
    ('PENDING', 'Pending'),
    ('ASSIGNED', 'Assigned'),
    ('IN_TRANSIT', 'In Transit'),
    ('DELIVERED', 'Delivered'),
    ('CANCELLED', 'Cancelled'),
)

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    pickup_address = models.ForeignKey(Address, related_name='pickup_orders', on_delete=models.CASCADE)
    delivery_address = models.ForeignKey(Address, related_name='delivery_orders', on_delete=models.CASCADE)
    contact_name = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='PENDING')
    assigned_driver = models.ForeignKey('Driver', null=True, blank=True, on_delete=models.SET_NULL)
    expected_delivery = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer} - {self.status}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.name} x{self.quantity}"

class Driver(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    vehicle_number = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    current_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.vehicle_number})"

class DeliveryUpdate(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='updates')
    status = models.CharField(max_length=20, choices=ORDER_STATUS)
    note = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.order} - {self.status} @ {self.timestamp}"
```

---

## 4) Admin registration (`delivery/admin.py`)

```python
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

admin.site.register(Customer)
admin.site.register(Address)
admin.site.register(Driver)
```

---

## 5) Forms (`delivery/forms.py`)

```python
from django import forms
from .models import Order, OrderItem, Address

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['street', 'city', 'state', 'pincode']

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['name', 'quantity', 'weight_kg']

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['contact_name', 'contact_phone', 'expected_delivery']
```

---

## 6) Views (`delivery/views.py`)

```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order, Customer, Address, OrderItem, DeliveryUpdate, Driver
from .forms import AddressForm, OrderCreateForm, OrderItemForm
from django.forms import formset_factory
from django.contrib import messages

@login_required
def dashboard(request):
    # Simple admin-like dashboard for staff
    if not request.user.is_staff:
        return redirect('order_list')
    orders = Order.objects.all().order_by('-created_at')[:50]
    drivers = Driver.objects.filter(is_active=True)
    return render(request, 'admin/dashboard.html', {'orders': orders, 'drivers': drivers})

@login_required
def order_create(request):
    # Customer places an order
    user = request.user
    customer, _ = Customer.objects.get_or_create(user=user, defaults={'phone': ''})

    AddressFormSet = formset_factory(AddressForm, extra=0)
    OrderItemFormSet = formset_factory(OrderItemForm, extra=1)

    if request.method == 'POST':
        pickup_form = AddressForm(request.POST, prefix='pickup')
        delivery_form = AddressForm(request.POST, prefix='delivery')
        order_form = OrderCreateForm(request.POST)
        items_formset = OrderItemFormSet(request.POST, prefix='items')

        if pickup_form.is_valid() and delivery_form.is_valid() and order_form.is_valid() and items_formset.is_valid():
            pickup = pickup_form.save(commit=False)
            pickup.customer = customer
            pickup.save()
            delivery = delivery_form.save(commit=False)
            delivery.customer = customer
            delivery.save()

            order = order_form.save(commit=False)
            order.customer = customer
            order.pickup_address = pickup
            order.delivery_address = delivery
            order.save()

            for item_form in items_formset:
                if item_form.cleaned_data.get('name'):
                    item = item_form.save(commit=False)
                    item.order = order
                    item.save()

            DeliveryUpdate.objects.create(order=order, status='PENDING', note='Order created')
            messages.success(request, f'Order #{order.id} created successfully')
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
    return render(request, 'customer/order_create.html', context)

@login_required
def order_list(request):
    user = request.user
    if request.user.is_staff:
        orders = Order.objects.all().order_by('-created_at')
    else:
        customer = Customer.objects.filter(user=user).first()
        orders = Order.objects.filter(customer=customer).order_by('-created_at')
    return render(request, 'customer/order_list.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    updates = order.updates.all()
    return render(request, 'customer/order_detail.html', {'order': order, 'updates': updates})

# Admin utilities: assign driver and update status (simple views)
from django.views.decorators.http import require_POST

@require_POST
@login_required
def assign_driver(request, order_id):
    if not request.user.is_staff:
        return redirect('order_list')
    order = get_object_or_404(Order, id=order_id)
    driver_id = request.POST.get('driver_id')
    driver = get_object_or_404(Driver, id=driver_id)
    order.assigned_driver = driver
    order.status = 'ASSIGNED'
    order.save()
    DeliveryUpdate.objects.create(order=order, status='ASSIGNED', note=f'Driver {driver.name} assigned')
    return redirect('dashboard')

@require_POST
@login_required
def update_status(request, order_id):
    if not request.user.is_staff:
        return redirect('order_list')
    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get('status')
    note = request.POST.get('note', '')
    if new_status in dict(Order._meta.get_field('status').choices).keys():
        order.status = new_status
        order.save()
        DeliveryUpdate.objects.create(order=order, status=new_status, note=note)
    return redirect('dashboard')
```

---

## 7) URLs

**Project `swift_delivery/urls.py`**

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('delivery.urls')),
]
```

**App `delivery/urls.py`**

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('orders/create/', views.order_create, name='order_create'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('orders/<int:order_id>/assign_driver/', views.assign_driver, name='assign_driver'),
    path('orders/<int:order_id>/update_status/', views.update_status, name='update_status'),
]
```

---

## 8) Templates (minimal examples)

**`delivery/templates/base.html`**

```html
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Swift Nationwide Delivery</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
<nav class="navbar navbar-expand-lg navbar-light bg-light mb-4">
  <div class="container">
    <a class="navbar-brand" href="/">Swift Nationwide Delivery</a>
    <div>
      {% if user.is_authenticated %}
        <a class="btn btn-outline-primary" href="/">Orders</a>
        <a class="btn btn-outline-secondary" href="/orders/create/">Create Order</a>
        {% if user.is_staff %}<a class="btn btn-warning" href="/dashboard/">Admin Dashboard</a>{% endif %}
        <a class="btn btn-link" href="/admin/logout/">Logout</a>
      {% else %}
        <a class="btn btn-primary" href="/admin/login/">Login</a>
      {% endif %}
    </div>
  </div>
</nav>
<div class="container">
  {% if messages %}
    {% for message in messages %}
      <div class="alert alert-info">{{ message }}</div>
    {% endfor %}
  {% endif %}
  {% block content %}{% endblock %}
</div>
</body>
</html>
```

**`delivery/templates/customer/order_create.html`**

```html
{% extends 'base.html' %}
{% load crispy_forms_tags %}
{% block content %}
<h2>Create Order</h2>
<form method="post">{% csrf_token %}
  <div class="row">
    <div class="col-md-6">
      <h4>Pickup Address</h4>
      {{ pickup_form|crispy }}
    </div>
    <div class="col-md-6">
      <h4>Delivery Address</h4>
      {{ delivery_form|crispy }}
    </div>
  </div>
  <hr>
  <h4>Order Details</h4>
  {{ order_form|crispy }}

  <h4>Items</h4>
  {{ items_formset.management_form }}
  {% for form in items_formset %}
    <div class="card mb-2 p-2">{{ form|crispy }}</div>
  {% endfor %}

  <button class="btn btn-success" type="submit">Place Order</button>
</form>
{% endblock %}
```

**`delivery/templates/customer/order_list.html`**

```html
{% extends 'base.html' %}
{% block content %}
<h2>Orders</h2>
<table class="table">
  <thead><tr><th>ID</th><th>Status</th><th>Created</th><th>Action</th></tr></thead>
  <tbody>
    {% for o in orders %}
      <tr>
        <td>{{ o.id }}</td>
        <td>{{ o.get_status_display }}</td>
        <td>{{ o.created_at }}</td>
        <td><a href="{% url 'order_detail' o.id %}" class="btn btn-sm btn-primary">View</a></td>
      </tr>
    {% empty %}
      <tr><td colspan="4">No orders found.</td></tr>
    {% endfor %}
  </tbody>
</table>
{% endblock %}
```

**`delivery/templates/customer/order_detail.html`**

```html
{% extends 'base.html' %}
{% block content %}
<h2>Order #{{ order.id }}</h2>
<p>Status: <strong>{{ order.get_status_display }}</strong></p>
<p>Pickup: {{ order.pickup_address }}</p>
<p>Delivery: {{ order.delivery_address }}</p>
<p>Assigned Driver: {{ order.assigned_driver }}</p>
<hr>
<h4>Updates</h4>
<ul class="list-group">
  {% for u in updates %}
    <li class="list-group-item">{{ u.timestamp }} — {{ u.get_status_display }} {% if u.note %}- {{ u.note }}{% endif %}</li>
  {% empty %}
    <li class="list-group-item">No updates</li>
  {% endfor %}
</ul>
{% endblock %}
```

**`delivery/templates/admin/dashboard.html`**

```html
{% extends 'base.html' %}
{% block content %}
<h2>Admin Dashboard</h2>
<h4>Recent Orders</h4>
<table class="table">
  <thead><tr><th>ID</th><th>Customer</th><th>Status</th><th>Driver</th><th>Actions</th></tr></thead>
  <tbody>
    {% for o in orders %}
      <tr>
        <td>{{ o.id }}</td>
        <td>{{ o.customer }}</td>
        <td>{{ o.get_status_display }}</td>
        <td>{{ o.assigned_driver }}</td>
        <td>
          <form method="post" action="{% url 'assign_driver' o.id %}" style="display:inline">{% csrf_token %}
            <select name="driver_id">
              {% for d in drivers %}
                <option value="{{ d.id }}">{{ d.name }}</option>
              {% endfor %}
            </select>
            <button class="btn btn-sm btn-primary">Assign</button>
          </form>
          <form method="post" action="{% url 'update_status' o.id %}" style="display:inline">{% csrf_token %}
            <select name="status">
              <option value="IN_TRANSIT">In Transit</option>
              <option value="DELIVERED">Delivered</option>
              <option value="CANCELLED">Cancelled</option>
            </select>
            <input name="note" placeholder="note" />
            <button class="btn btn-sm btn-warning">Update</button>
          </form>
        </td>
      </tr>
    {% endfor %}
  </tbody>
</table>
{% endblock %}
```

---

## 9) Authentication and user creation

- This scaffold uses Django `User` for auth. Customers are `User` with a related `Customer` profile.
- Use Django admin to create customers or let them sign up via a registration view (not included; you can use `django-allauth` or create a simple signup form that creates `User` and `Customer`).

---

## 10) Migrations & running

```bash
python manage.py makemigrations delivery
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## 11) Tips & extensions (how to make it production-ready)
- Use HTTPS and secure DB credentials via environment variables.
- Add REST API endpoints (Django REST Framework) for mobile/web frontend.
- Add WebSocket or polling to push delivery updates (channels or third-party services).
- Add mapping: integrate Google Maps or Leaflet to show driver location (`current_lat`, `current_lng`).
- Use Celery for background tasks (notifications, ETA recalculation).
- Add tests for models and views.

---

## 12) Troubleshooting SQL Server connection
- If you get ODBC driver errors, ensure the driver name in `OPTIONS['driver']` matches the installed ODBC driver.
- On Windows, make sure to install the matching 64-bit ODBC driver for your Python bitness.
- If using trusted connection, set `OPTIONS: {'driver': 'ODBC Driver 18 for SQL Server', 'extra_params': 'Trusted_Connection=yes;'}` or adjust USER/PASSWORD.

---

## 13) Next steps I can help with
- Add user registration & login pages.
- Implement an API with Django REST Framework.
- Add live driver tracking on the order detail page (map + periodic updates).
- Add email/SMS notifications when status changes.

---

### That's it — quick checklist to get started
1. Install Python, SQL Server, ODBC driver.
2. Create DB `swift_delivery_db`.
3. Create virtualenv, install requirements.
4. Place files in project structure shown above.
5. Configure `settings.py` DB and `INSTALLED_APPS`.
6. Run `makemigrations` & `migrate`.
7. Create superuser and start server.


---

If you'd like, I can now:
- generate the full code as separate downloadable files (one zip), or
- add user signup, or
- convert the admin dashboard into a React frontend.

Tell me which next feature you want and I'll add it to the project.


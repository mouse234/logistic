# Swift Nationwide Delivery - Logistics Management System

A complete Django-based logistics management system with customer order tracking, admin dashboard, and driver management capabilities.

## Features

### Customer Features
- ✅ User registration and authentication
- ✅ Create new delivery orders with pickup and delivery addresses
- ✅ Track order status in real-time
- ✅ View order history and details
- ✅ Multiple items per order support
- ✅ Contact information management

### Admin Features
- ✅ Comprehensive admin dashboard with statistics
- ✅ Order management (view, assign drivers, update status)
- ✅ Driver management with vehicle tracking
- ✅ Customer management
- ✅ Real-time status updates with notes and location
- ✅ Django admin integration for advanced management

### Driver Features
- ✅ Driver profiles with contact information
- ✅ Vehicle assignment and tracking
- ✅ Location tracking (latitude/longitude support)
- ✅ Active/inactive status management

## Technology Stack

- **Backend**: Django 5.2.6 (Python)
- **Database**: SQLite (for demo/development)
- **Frontend**: Bootstrap 5.3.0 + HTML/CSS
- **Forms**: Django Crispy Forms with Bootstrap 4 styling
- **Icons**: Bootstrap Icons

## Quick Start

### Prerequisites
- Python 3.10+ installed
- Virtual environment (recommended)

### Installation & Setup

1. **Activate virtual environment** (already set up):
   ```bash
   venv\Scripts\activate  # Windows
   # or source venv/bin/activate  # Linux/Mac
   ```

2. **Install dependencies** (already installed):
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations** (already done):
   ```bash
   python manage.py migrate
   ```

4. **Create dummy data** (already created):
   ```bash
   python manage.py create_dummy_data
   ```

5. **Start the development server**:
   ```bash
   python manage.py runserver
   ```

6. **Access the application**:
   - Main site: http://127.0.0.1:8000/
   - Django Admin: http://127.0.0.1:8000/admin/

## Login Credentials

### Admin Access
- **Username**: admin
- **Password**: admin123
- **Access**: Full admin dashboard + Django admin

### Customer Accounts
- **Username**: john_doe, jane_smith, mike_johnson, sarah_wilson, david_brown
- **Password**: password123 (for all customers)
- **Access**: Customer portal for order creation and tracking

## Demo Data

The system comes pre-loaded with:
- 🔸 **5 Customer accounts** with complete profiles
- 🔸 **5 Drivers** with vehicles and location data
- 🔸 **10 Addresses** across different US cities
- 🔸 **5 Sample orders** in various stages:
  - 1 Delivered order (with full tracking history)
  - 1 In-transit order (with driver assigned)
  - 1 Assigned order (driver assigned, awaiting pickup)
  - 2 Pending orders (awaiting driver assignment)

## Project Structure

```
logistics/
├── delivery/                    # Main Django app
│   ├── migrations/              # Database migrations
│   ├── management/              # Custom management commands
│   │   └── commands/
│   │       └── create_dummy_data.py
│   ├── templates/               # HTML templates
│   │   ├── delivery/
│   │   │   ├── admin/          # Admin dashboard templates
│   │   │   ├── customer/       # Customer portal templates
│   │   │   ├── base.html       # Base template
│   │   │   └── home.html       # Homepage
│   │   └── registration/        # Auth templates
│   ├── static/                  # Static files (CSS, JS, images)
│   ├── admin.py                 # Django admin configuration
│   ├── forms.py                 # Django forms
│   ├── models.py                # Database models
│   ├── urls.py                  # App URL patterns
│   └── views.py                 # View functions
├── swift_delivery/              # Django project settings
│   ├── settings.py              # Project configuration
│   ├── urls.py                  # Main URL patterns
│   └── wsgi.py                  # WSGI configuration
├── db.sqlite3                   # SQLite database
├── manage.py                    # Django management script
└── requirements.txt             # Python dependencies
```

## Key Models

### Customer
- Linked to Django User model
- Phone number
- Multiple addresses support

### Order
- Customer information
- Pickup and delivery addresses
- Contact details
- Status tracking (PENDING → ASSIGNED → IN_TRANSIT → DELIVERED)
- Driver assignment
- Expected delivery date

### Driver
- Personal information
- Vehicle details
- GPS coordinates (current location)
- Active/inactive status

### DeliveryUpdate
- Real-time status updates
- Notes and location information
- Timestamp tracking

## API Endpoints

### Public Routes
- `/` - Homepage
- `/register/` - User registration
- `/login/` - User login
- `/logout/` - User logout

### Customer Routes (Login Required)
- `/orders/` - Order list
- `/orders/create/` - Create new order
- `/orders/<id>/` - Order details and tracking

### Admin Routes (Staff Required)
- `/dashboard/` - Admin dashboard with statistics
- `/orders/<id>/assign_driver/` - Assign driver to order
- `/orders/<id>/update_status/` - Update order status

## Customization Options

### Database
- Currently using SQLite for demo
- Can be easily changed to PostgreSQL, MySQL, or SQL Server
- Update `DATABASES` setting in `settings.py`

### Styling
- Bootstrap 5.3.0 for responsive design
- Custom CSS can be added to `/static/delivery/css/`
- Color scheme and branding easily customizable

### Features to Add
- 📧 Email notifications
- 📱 SMS alerts
- 🗺️ Interactive map integration
- 📊 Advanced analytics
- 💳 Payment integration
- 📱 Mobile app API
- 🔄 Real-time WebSocket updates

## Development Commands

```bash
# Create new migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser account
python manage.py createsuperuser

# Collect static files for production
python manage.py collectstatic

# Run tests
python manage.py test

# Access Django shell
python manage.py shell
```

## Production Deployment

For production deployment:

1. **Change SECRET_KEY** in settings.py
2. **Set DEBUG = False**
3. **Configure proper database** (PostgreSQL recommended)
4. **Set up static file serving**
5. **Configure ALLOWED_HOSTS**
6. **Use WSGI server** (Gunicorn + Nginx)
7. **Set up HTTPS**
8. **Configure environment variables**

## Support & Documentation

- Django Documentation: https://docs.djangoproject.com/
- Bootstrap Documentation: https://getbootstrap.com/docs/
- Project built following Django best practices

## License

This project is created for demonstration purposes. Feel free to modify and extend according to your needs.

---

**Built with ❤️ using Django + Bootstrap**
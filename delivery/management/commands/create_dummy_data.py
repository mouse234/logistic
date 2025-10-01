from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from delivery.models import Customer, Address, Order, OrderItem, Driver, DeliveryUpdate
from datetime import datetime, timedelta
from django.utils import timezone


class Command(BaseCommand):
    help = 'Create dummy data for Swift Delivery demo'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating dummy data...'))

        # Create superuser
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@swiftdelivery.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(self.style.SUCCESS('✓ Created admin user (username: admin, password: admin123)'))
        
        # Create regular users and customers
        users_data = [
            {'username': 'john_doe', 'first_name': 'John', 'last_name': 'Doe', 'email': 'john@example.com', 'phone': '+1-555-0101'},
            {'username': 'jane_smith', 'first_name': 'Jane', 'last_name': 'Smith', 'email': 'jane@example.com', 'phone': '+1-555-0102'},
            {'username': 'mike_johnson', 'first_name': 'Mike', 'last_name': 'Johnson', 'email': 'mike@example.com', 'phone': '+1-555-0103'},
            {'username': 'sarah_wilson', 'first_name': 'Sarah', 'last_name': 'Wilson', 'email': 'sarah@example.com', 'phone': '+1-555-0104'},
            {'username': 'david_brown', 'first_name': 'David', 'last_name': 'Brown', 'email': 'david@example.com', 'phone': '+1-555-0105'},
        ]

        customers = []
        for user_data in users_data:
            if not User.objects.filter(username=user_data['username']).exists():
                user = User.objects.create_user(
                    username=user_data['username'],
                    password='password123',
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    email=user_data['email']
                )
                customer = Customer.objects.create(user=user, phone=user_data['phone'])
                customers.append(customer)
                self.stdout.write(f'✓ Created user and customer: {user.get_full_name()}')

        # Get existing customers if any
        if not customers:
            customers = list(Customer.objects.all())

        # Create drivers
        drivers_data = [
            {'name': 'Robert Garcia', 'phone': '+1-555-1001', 'vehicle_number': 'TRK-001', 'lat': 40.7128, 'lng': -74.0060},
            {'name': 'Maria Rodriguez', 'phone': '+1-555-1002', 'vehicle_number': 'TRK-002', 'lat': 34.0522, 'lng': -118.2437},
            {'name': 'James Wilson', 'phone': '+1-555-1003', 'vehicle_number': 'TRK-003', 'lat': 41.8781, 'lng': -87.6298},
            {'name': 'Lisa Anderson', 'phone': '+1-555-1004', 'vehicle_number': 'VAN-101', 'lat': 29.7604, 'lng': -95.3698},
            {'name': 'Michael Davis', 'phone': '+1-555-1005', 'vehicle_number': 'VAN-102', 'lat': 33.4484, 'lng': -112.0740},
        ]

        drivers = []
        for driver_data in drivers_data:
            if not Driver.objects.filter(name=driver_data['name']).exists():
                driver = Driver.objects.create(
                    name=driver_data['name'],
                    phone=driver_data['phone'],
                    vehicle_number=driver_data['vehicle_number'],
                    current_lat=driver_data['lat'],
                    current_lng=driver_data['lng'],
                    is_active=True
                )
                drivers.append(driver)
                self.stdout.write(f'✓ Created driver: {driver.name} ({driver.vehicle_number})')

        # Get existing drivers if any
        if not drivers:
            drivers = list(Driver.objects.all())

        # Create addresses for each customer
        addresses_data = [
            {'street': '123 Main St', 'city': 'New York', 'state': 'NY', 'pincode': '10001'},
            {'street': '456 Oak Ave', 'city': 'Los Angeles', 'state': 'CA', 'pincode': '90210'},
            {'street': '789 Pine Rd', 'city': 'Chicago', 'state': 'IL', 'pincode': '60601'},
            {'street': '321 Elm St', 'city': 'Houston', 'state': 'TX', 'pincode': '77001'},
            {'street': '654 Maple Dr', 'city': 'Phoenix', 'state': 'AZ', 'pincode': '85001'},
            {'street': '987 Cedar Ln', 'city': 'Philadelphia', 'state': 'PA', 'pincode': '19101'},
            {'street': '147 Birch St', 'city': 'San Antonio', 'state': 'TX', 'pincode': '78201'},
            {'street': '258 Spruce Ave', 'city': 'San Diego', 'state': 'CA', 'pincode': '92101'},
            {'street': '369 Willow Way', 'city': 'Dallas', 'state': 'TX', 'pincode': '75201'},
            {'street': '741 Poplar Pl', 'city': 'San Jose', 'state': 'CA', 'pincode': '95101'},
        ]

        addresses = []
        for i, addr_data in enumerate(addresses_data):
            customer = customers[i % len(customers)] if customers else None
            if customer:
                address = Address.objects.create(
                    customer=customer,
                    street=addr_data['street'],
                    city=addr_data['city'],
                    state=addr_data['state'],
                    pincode=addr_data['pincode']
                )
                addresses.append(address)

        self.stdout.write(f'✓ Created {len(addresses)} addresses')

        # Create sample orders
        if customers and addresses and len(addresses) >= 2:
            orders_data = [
                {
                    'customer': customers[0],
                    'pickup_idx': 0, 'delivery_idx': 1,
                    'contact_name': 'John Doe', 'contact_phone': '+1-555-0101',
                    'status': 'DELIVERED', 'driver': drivers[0] if drivers else None,
                    'items': [{'name': 'Electronics Package', 'quantity': 1, 'weight': 2.5}],
                    'days_ago': 5
                },
                {
                    'customer': customers[1] if len(customers) > 1 else customers[0],
                    'pickup_idx': 2, 'delivery_idx': 3,
                    'contact_name': 'Jane Smith', 'contact_phone': '+1-555-0102',
                    'status': 'IN_TRANSIT', 'driver': drivers[1] if len(drivers) > 1 else drivers[0],
                    'items': [
                        {'name': 'Books', 'quantity': 3, 'weight': 1.2},
                        {'name': 'Documents', 'quantity': 1, 'weight': 0.5}
                    ],
                    'days_ago': 2
                },
                {
                    'customer': customers[2] if len(customers) > 2 else customers[0],
                    'pickup_idx': 4, 'delivery_idx': 5,
                    'contact_name': 'Mike Johnson', 'contact_phone': '+1-555-0103',
                    'status': 'ASSIGNED', 'driver': drivers[2] if len(drivers) > 2 else drivers[0],
                    'items': [{'name': 'Furniture Parts', 'quantity': 1, 'weight': 15.0}],
                    'days_ago': 1
                },
                {
                    'customer': customers[3] if len(customers) > 3 else customers[0],
                    'pickup_idx': 6, 'delivery_idx': 7,
                    'contact_name': 'Sarah Wilson', 'contact_phone': '+1-555-0104',
                    'status': 'PENDING', 'driver': None,
                    'items': [
                        {'name': 'Clothing', 'quantity': 2, 'weight': 0.8},
                        {'name': 'Shoes', 'quantity': 1, 'weight': 1.0}
                    ],
                    'days_ago': 0
                },
                {
                    'customer': customers[4] if len(customers) > 4 else customers[0],
                    'pickup_idx': 8, 'delivery_idx': 9,
                    'contact_name': 'David Brown', 'contact_phone': '+1-555-0105',
                    'status': 'PENDING', 'driver': None,
                    'items': [{'name': 'Computer Equipment', 'quantity': 1, 'weight': 5.5}],
                    'days_ago': 0
                }
            ]

            for order_data in orders_data:
                pickup_addr = addresses[order_data['pickup_idx']]
                delivery_addr = addresses[order_data['delivery_idx']]
                created_time = timezone.now() - timedelta(days=order_data['days_ago'])
                
                order = Order.objects.create(
                    customer=order_data['customer'],
                    pickup_address=pickup_addr,
                    delivery_address=delivery_addr,
                    contact_name=order_data['contact_name'],
                    contact_phone=order_data['contact_phone'],
                    status=order_data['status'],
                    assigned_driver=order_data['driver'],
                    created_at=created_time,
                    expected_delivery=created_time + timedelta(days=3)
                )

                # Create order items
                for item_data in order_data['items']:
                    OrderItem.objects.create(
                        order=order,
                        name=item_data['name'],
                        quantity=item_data['quantity'],
                        weight_kg=item_data['weight']
                    )

                # Create delivery updates based on status
                self.create_delivery_updates(order, created_time)
                
                self.stdout.write(f'✓ Created order #{order.id} ({order.status})')

        self.stdout.write(self.style.SUCCESS('\\n🎉 Dummy data creation completed!'))
        self.stdout.write(self.style.SUCCESS('\n🎉 Dummy data creation completed!'))
        self.stdout.write(self.style.SUCCESS('\n📝 Login credentials:'))
        self.stdout.write(self.style.SUCCESS('   Admin: username=admin, password=admin123'))
        self.stdout.write(self.style.SUCCESS('   Users: username=john_doe (or any other), password=password123'))
        self.stdout.write(self.style.SUCCESS('\n🚀 Start the server with: python manage.py runserver'))

    def create_delivery_updates(self, order, created_time):
        """Create delivery updates based on order status"""
        updates = []
        
        # Always create initial update
        updates.append({
            'status': 'PENDING',
            'note': 'Order created and awaiting assignment',
            'timestamp': created_time
        })

        if order.status in ['ASSIGNED', 'IN_TRANSIT', 'DELIVERED']:
            updates.append({
                'status': 'ASSIGNED',
                'note': f'Driver {order.assigned_driver.name} assigned to this order',
                'timestamp': created_time + timedelta(hours=2)
            })

        if order.status in ['IN_TRANSIT', 'DELIVERED']:
            updates.append({
                'status': 'IN_TRANSIT',
                'note': 'Package picked up and in transit',
                'location': f'{order.pickup_address.city}, {order.pickup_address.state}',
                'timestamp': created_time + timedelta(hours=4)
            })

        if order.status == 'DELIVERED':
            updates.append({
                'status': 'DELIVERED',
                'note': 'Package delivered successfully',
                'location': f'{order.delivery_address.city}, {order.delivery_address.state}',
                'timestamp': created_time + timedelta(days=1)
            })

        for update_data in updates:
            DeliveryUpdate.objects.create(
                order=order,
                status=update_data['status'],
                note=update_data['note'],
                location=update_data.get('location', ''),
                timestamp=update_data['timestamp']
            )
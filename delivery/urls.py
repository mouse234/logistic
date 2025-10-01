from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Home and authentication
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    
    # Customer views
    path('orders/', views.order_list, name='order_list'),
    path('orders/create/', views.order_create, name='order_create'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    
    # Admin views
    path('dashboard/', views.dashboard, name='dashboard'),
    path('orders/<int:order_id>/assign_driver/', views.assign_driver, name='assign_driver'),
    path('orders/<int:order_id>/update_status/', views.update_status, name='update_status'),
]
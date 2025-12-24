from django.urls import path
from .views import *

app_name= 'accounts'

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='user_register'),
    path('verify/', UserRegisterVerifyCodeView.as_view(), name='verify_code'),
    path('login/', UserLoginView.as_view(), name='user_login'),
    path('logout/', UserLogoutView.as_view(), name='user_logout'),
    path('profile/<int:user_id>/', UserProfileView.as_view(), name='user_profile'),
    path('reset/', UserPasswordResetView.as_view() , name='reset_password'),
    path('reset/done/', UserPasswordResetDoneView.as_view(), name='password_reset_done' ),
    path('confirm/<uidb64>/<token>/', UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('confirm/complete/', UserPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('my-info/', UserDetailsView.as_view(), name='user_details'),
    path('my-orders/', UserOrdersView.as_view(), name='user_orders'),
    path('my-addresses/', UserAddressView.as_view(), name='user_addresses'),
    path('my-addresses/create/', AddressCreateView.as_view(), name='address_create'),
    path('my-addresses/<int:address_id>/edit/', AddressUpdateView.as_view(), name='address_edit'),
    path('my-addresses/<int:address_id>/delete/', AddressDeleteView.as_view(), name='address_delete'),
    path('my-addresses/<int:address_id>/set-default/', SetDefaultAddressView.as_view(), name='set_default_address'),
]

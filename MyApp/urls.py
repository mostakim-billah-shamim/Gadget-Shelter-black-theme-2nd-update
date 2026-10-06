from django.urls import path
from .views import *

urlpatterns = [
    path('login/', loginPage, name='login'),
    path('registration/', registerPage, name='register'),
    path('logout/', logoutPage, name='logout'),
    path('change-password/', change_password, name='change_password'),



    
    path('', HomePage, name='index'),
    


    
    path('cart/', CartPage, name='cart'),
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', remove_from_cart, name='remove_cart'),



    path('contact/', ContactPage, name='contact'),
    path('contact_message_list/', contact_message_list, name='contact_message_list'),
    path('toggle_message_done/<int:pk>/', toggle_message_done, name='toggle_message_done'),
    path('delete_contact_message/<int:pk>/', delete_contact_message, name='delete_contact_message'),


   
    

    # Wishlist URLs
    path('wishlist/', wishlist_view, name='wishlist'),
    path('wishlist/add/<int:product_id>/', add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', remove_from_wishlist, name='remove_from_wishlist'),

    # Compare URLs
    path('compare/', compare_view, name='compare'),
    path('compare/add/<int:product_id>/', add_to_compare, name='add_to_compare'),
    path('compare/remove/<int:product_id>/', remove_from_compare, name='remove_from_compare'),


    path('shop/', ShopPage, name='shop'),
    path('single/<int:pk>/', SinglePage, name='single'),
    





    path('checkout/', checkout_page, name='checkout'),
    path('order-success/<str:order_id>/', order_success, name='order_success'),
    path('track-order/', track_order, name='track_order'),
]
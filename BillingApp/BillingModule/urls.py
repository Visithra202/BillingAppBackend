from django.urls import path
from .views import *

urlpatterns=[
    path('get-logo/', get_logo, name='get_logo'),

    # Category
    path('add-category/', add_category, name='add_category'),
    path('get-category-list/', get_category_list, name='get_category_list'),
    path('delete-category/<int:category_id>/', delete_category, name='delete_category'),

    # Brand
    path('add-brand/', add_brand, name='add_brand'),
    path('get-brand-list/', get_brand_list, name='get_brand_list'),
    path('delete-brand/<int:brand_id>/', delete_brand, name='delete_brand'),

    #Item
    path('add-item/',add_item, name='add_item'),
    path('get-stock-list/', get_stock_list, name='get_stock_list'),
    path('delete-item/<int:item_id>/', delete_item, name='delete_item'),
    path('edit-item/<int:item_id>/', edit_item, name='edit_item' ),

    # Customer
    path('add-customer/',add_customer, name='add_customer'),
    path('get-customer-list/', get_customer_list, name='get_customer_list'),
    path('delete-customer/<int:customer_id>/', delete_customer, name='delete_customer'),

    # Seller
    path('add-seller/',add_seller, name='add_seller'),
    path('get-seller-list/', get_seller_list, name='get_seller_list'),
    path('delete-seller/<int:seller_id>/', delete_seller, name='delete_seller'),

    # Sale bill
    path('get-sale-bill-no/', get_sale_bill_no, name='get_sale_bill_no'),

    # Sale bill
    path('get-purchase-bill-no/', get_purchase_bill_no, name='get_purchase_bill_no'),

    # Sale
    path('add-sale/', add_sale, name='add_sale'),
    path('get-sale-list/', get_sale_list, name='get_sale_list'),
    path('get-sale-items-list/', get_sale_items_list, name='get_sale_items_list'),
    path('delete-sale/<int:bill_no>/', delete_sale, name='delete_sale'),

    # payments
    path('get-payment-list/', get_payment_list, name='get_payment_list'),
    
    # Loan
    path('create-loan/', create_loan, name='create_loan'),
    path('get-loan-list/', get_loan_list, name='get_loan_list'),
    path('get-collection-list/', get_collection_list, name='get_collection_list'),
    path('get-loan-bill/<str:loan_accno>', get_loan_bill, name='get_loan_bill'),
    path('add-loan-payment/', add_loan_payment, name='add_loan_payment'),
    path('get-loan-journal/<str:loan_accno>/', get_loan_journal, name='get_loan_journal'),
    
    # Purchase
    path('add-purchase/', add_purchase, name='add_purchase'),
    path('get-purchase-list/', get_purchase_list, name='get_purchase_list'),
    path('get-purchase-items-list/', get_purchase_items_list, name='get_purchase_items_list'),
    path('get-purchase-payment-list/', get_purchase_payment_list, name='get_purchase_payment_list'),
    
    path('user-login/', user_login, name='user_login'),
    path('add-user/', add_user, name='add_user'),
    path('get-user-list/', get_user_list, name='get_user_list'),
    path('delete-user/<int:user_id>/', delete_user, name='delete_user'),
]
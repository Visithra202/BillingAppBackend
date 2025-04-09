from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializer import *
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password



@api_view(['GET'])
def get_logo(request):
    compdet = Compdet.objects.first()
    if not compdet:
        return Response({"error": "No logo found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = CompdetSerializer(compdet)
    return Response(serializer.data, status=status.HTTP_200_OK)

# Category
@api_view(['POST'])
def add_category(request):
    serializer=CategorySerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(serializer.data, status=200)
    
@api_view(['GET'])
def get_category_list(request):
    categories=Category.objects.all()
    serializer=CategorySerializer(categories, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['DELETE'])
def delete_category(request, category_id):
    category=get_object_or_404(Category,category_id=category_id)
    category.delete()
    return Response({"message": "Category deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


#Brand
@api_view(['GET'])
def get_brand_list(request):
    brands=Brand.objects.all()
    serializer = BrandSerializer(brands, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def add_brand(request):
    serializer= BrandSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(serializer.data, status=200)
    
@api_view(['DELETE'])
def delete_brand(request, brand_id):
    brand=get_object_or_404(Brand,brand_id=brand_id)
    brand.delete()
    return Response({"message": "Brand deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


#Item
@api_view(['POST'])
def add_item(request):
    serializer= ItemSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        item = serializer.save()
        return Response(serializer.data, status=200)
    
@api_view(['GET'])
def get_stock_list(request):
    items=Item.objects.all()
    serializer = ItemSerializer(items, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['DELETE'])
def delete_item(request, item_id):
    item=get_object_or_404(Item,item_id=item_id)
    item.delete()
    return Response({"message": "Item deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

@api_view(['PUT'])
def edit_item(request, item_id):  
    item = get_object_or_404(Item, item_id=item_id)
    print(request.data)
    serializer = ItemSerializer(item, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        print(serializer.errors) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Customer
@api_view(['POST'])
def add_customer(request):
    serializer= CustomerSerializer(data=request.data)
    if serializer.is_valid():
        item = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    print(serializer.data)
    print(serializer.errors)
    return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    
@api_view(['GET'])
def get_customer_list(request):
    customers=Customer.objects.all()
    serializer = CustomerSerializer(customers, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['DELETE'])
def delete_customer(request, customer_id):
    customer=get_object_or_404(Customer,customer_id=customer_id)
    customer.delete()
    return Response({"message": "Customer deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

    
@api_view(['GET'])
def get_sale_bill_no(request):
    current_year=now().year
    prefix=f'BILL-{current_year}-'

    bill=SaleBill.objects.filter(bill_year=current_year).first()

    if bill:
        nex_seq=bill.bill_seq + 1
    else:
        nex_seq=1
    
    bill_no=f'{prefix}{nex_seq}'
    return JsonResponse({'bill_no':bill_no})


# Sale
@api_view(['POST'])
def add_sale(request):
    serializer=SaleSerializer(data=request.data)
    print(request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    print(serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_sale_list(request):
    sales=Sale.objects.all().order_by('sale_seq')
    serializer = SaleSerializer(sales, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['DELETE'])
def delete_sale(request, bill_no):
    sale=get_object_or_404(Sale,bill_no=bill_no)
    sale.delete()
    return Response({"message": "Item deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def get_sale_items_list(request):
    sales = SaleItem.objects.all()
    serializer = SaleItemSerializer(sales, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# Payments
@api_view(['GET'])
def get_payment_list(request):
    payments=Payment.objects.all()
    serializer = PaymentSerializer(payments, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Loan
@api_view(['POST'])
def create_loan(request):
    serializer=LoanSerializer(data=request.data)
    print(request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    print(serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_loan_list(request):
    loanList=Loan.objects.all()
    serializer = LoanSerializer(loanList, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# Purchase
@api_view(['POST'])
def add_purchase(request):
    serializer=PurchaseSerializer(data=request.data)
    print(request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    print(serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_purchase_list(request):
    purchase=Purchase.objects.all().order_by('purchase_seq')
    serializer = PurchaseSerializer(purchase, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_purchase_items_list(request):
    purchase=PurchaseItem.objects.all()
    serializer = PurchaseItemSerializer(purchase, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# Payments
@api_view(['GET'])
def get_purchase_payment_list(request):
    payments=PurchasePayment.objects.all()
    serializer = PurchasePaymentSerializer(payments, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)



# seller
@api_view(['POST'])
def add_seller(request):
    serializer= SellerSerializer(data=request.data)
    if serializer.is_valid():
        seller = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    print(serializer.data)
    print(serializer.errors)
    return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    
@api_view(['GET'])
def get_seller_list(request):
    sellers=Seller.objects.all()
    serializer = SellerSerializer(sellers, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['DELETE'])
def delete_seller(request, seller_id):
    seller=get_object_or_404(Seller,seller_id=seller_id)
    seller.delete()
    return Response({"message": "Seller deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

# Purchase bill no
@api_view(['GET'])
def get_purchase_bill_no(request):
    current_year=now().year
    prefix=f'PUR-{current_year}-'

    bill=PurchaseBill.objects.filter(bill_year=current_year).first()

    if bill:
        nex_seq=bill.bill_seq + 1
    else:
        nex_seq=1
    
    bill_no=f'{prefix}{nex_seq}'
    return JsonResponse({'bill_no':bill_no})


# Users

@api_view(['POSt'])
def user_login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    print(username + " "+ password)
    user = authenticate(username=username, password=password)
    print(user)
    if user:
        return Response({"message": "Login successful!"}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def add_user(request):
    username = request.data.get("username")
    password = request.data.get("password")
    confirm_password = request.data.get("confirm_password")

    if not username or not password:
        return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

    if password != confirm_password:
        return Response({"error": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already exists."}, status=status.HTTP_409_CONFLICT)

    User.objects.create(username=username, password=make_password(password))

    return Response({"message": "User created successfully!"}, status=status.HTTP_201_CREATED)


# Get Users
@api_view(['GET'])
def get_user_list(request):
    users = User.objects.all().values("id", "username")
    user_list = [{"user_id": u["id"], "username": u["username"]} for u in users]
    return Response(user_list, status=status.HTTP_200_OK)


# Delete User
@api_view(['DELETE'])
def delete_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        user.delete()
        return Response({"message": "User deleted successfully!"}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
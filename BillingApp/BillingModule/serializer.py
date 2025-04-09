from rest_framework import serializers
from .models import *
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.timezone import now
from datetime import timedelta
from datetime import datetime


class CompdetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compdet
        fields = ['logo_path']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        
class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['item_id', 'item_name', 'category', 'brand', 'quantity',
                  'min_stock', 'purchase_price', 'sale_price', 'tax_option',
                  'mrp', 'discount_type', 'discount']
        read_only_fields = ['item_id'] 

    def validate(self, data):
        if data['sale_price'] > data['mrp']:
            raise serializers.ValidationError("Sale price cannot be greater than MRP.")
        
        if data['sale_price']< data['purchase_price']:
            raise serializers.ValidationError('Purchase price cannot be greater than sale price.')
        return data
    
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class SaleBillSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleBill
        fields='__all__'

class PurchaseBillSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseBill
        fields='__all__'


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'



class TransactionItemSerializer(serializers.ModelSerializer):
    product=ItemSerializer()
    
    class Meta:
        fields = ['product', 'item_seq', 'quantity', 'unit_price', 'total_price']
        abstract = True  


class SaleItemSerializer(TransactionItemSerializer):
    sale = serializers.PrimaryKeyRelatedField(read_only=True)  
    
    class Meta(TransactionItemSerializer.Meta):
        model = SaleItem
        fields = TransactionItemSerializer.Meta.fields + ['sale']
        extra_kwargs = {'sale': {'required': False}}
        
class PurchaseItemSerializer(TransactionItemSerializer):
    purchase = serializers.PrimaryKeyRelatedField(read_only=True)  
    
    class Meta(TransactionItemSerializer.Meta):
        model = PurchaseItem
        fields = TransactionItemSerializer.Meta.fields + ['purchase']
        extra_kwargs = {'purchase': {'required': False}}
        

class PurchasePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model=PurchasePayment
        fields='__all__'
        
class SaleSerializer(serializers.ModelSerializer):
    sale_products = SaleItemSerializer(many=True, source='sale_items')
    payment = PaymentSerializer()
    customer=CustomerSerializer()

    class Meta:
        model = Sale
        fields = ['bill_no', 'sale_date', 'customer', 'payment', 'total_amount', 'discount', 'sale_products', 'balance']

    def create(self, validated_data):
        current_year = datetime.now().year

        bill, created = SaleBill.objects.get_or_create(
            bill_year=current_year,  
            defaults={'bill_seq': 1}  
        )

        if not created:
            bill.bill_seq += 1  
            bill.save()

        sale_products_data = validated_data.pop('sale_items', [])
        payment_data = validated_data.pop('payment', {})
        customer_data= validated_data.pop('customer', {})
        
        payment = Payment.objects.create(**payment_data)
        customer, created = Customer.objects.get_or_create(**customer_data)
        sale = Sale.objects.create(payment=payment, customer=customer, sale_seq=bill.bill_seq-1,  **validated_data)

        for index, product_data in enumerate(sale_products_data):
            
            item=Item.objects.get(item_id=product_data['product'].item_id)

            if (item.quantity>=product_data['quantity']):
                item.quantity-=product_data['quantity']
                item.save()
                saleItem=SaleItem.objects.create(sale=sale, item_seq=index + 1, **product_data)  
            else:
                raise serializers.ValidationError(f"Not enough stock for {item.item_name}")

          
        return sale

# class SaleSerializer(serializers.ModelSerializer):
#     customer = CustomerSerializer()
#     payment = PaymentSerializer()
#     sale_products = SaleItemSerializer(many=True, source='sale_items')

#     class Meta:
#         model = Sale
#         fields ='__all__'

#     def create(self, validated_data):
#         # Extract nested data
#         customer_data = validated_data.pop('customer')
#         payment_data = validated_data.pop('payment')
#         sale_items_data = validated_data.pop('sale_items', [])

#         # Create or get related objects
#         customer, _ = Customer.objects.get_or_create(**customer_data)
#         payment = Payment.objects.create(**payment_data)
        
#         sale = Sale.objects.create(customer=customer, payment=payment, **validated_data)

#         for item_data in sale_items_data:
#             product_data = item_data.pop('product')
#             print(payment_data)
#             product = Item.objects.get(item_id=product_data['item_id'])
#             SaleItem.objects.create(sale=sale, product=product, **item_data)

#         return sale



class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = '__all__'

class PurchaseSerializer(serializers.ModelSerializer):
    purchase_products=PurchaseItemSerializer(many=True, source='purchase_items')
    purchase_payment=PurchasePaymentSerializer()
    seller=SellerSerializer()
    
    class Meta:
        model = Purchase
        fields = ['purchase_id', 'purchase_date', 'seller', 'purchase_payment', 'total_amount', 'discount', 'purchase_products', 'balance']
    
    def create(self, validated_data):
        current_year=datetime.now().year
        
        bill, created=PurchaseBill.objects.get_or_create(
            bill_year = current_year,
            defaults= {'bill_seq':1}
        )
        
        if not created:
            bill.bill_seq+=1
            bill.save()
            
        purchase_products_data=validated_data.pop('purchase_items', [])
        payment_data=validated_data.pop('purchase_payment', {})
        seller_data=validated_data.pop('seller', {})
        
        purchase_payment=PurchasePayment.objects.create(**payment_data)
        seller, created=Seller.objects.get_or_create(**seller_data)
        purchase=Purchase.objects.create(purchase_payment=purchase_payment, seller=seller, purchase_seq=bill.bill_seq-1, **validated_data)
        
        for index, product_data in enumerate(purchase_products_data):
            item=Item.objects.get(item_id=product_data['product'].item_id)
            item.quantity+=product_data['quantity']
            item.save()
            purchaseItem=PurchaseItem.objects.create(purchase=purchase, item_seq=index+1, **product_data)
            
        
        return purchase
    
        
class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = '__all__'


class LoanSerializer(serializers.ModelSerializer):
    customer= CustomerSerializer()
    
    class Meta:
        model = Loan
        fields = '__all__'
        read_only_fields = ['loan_accno']  

    def create(self, validated_data):
        """Creates a Loan and auto-generates LoanBill entries"""
        today = date.today().strftime("%Y%m%d")  
        last_loan = Loan.objects.filter(loan_accno__startswith=today).order_by('-loan_accno').first()

        if last_loan:
            last_seq = int(last_loan.loan_accno[-3:])  
            new_seq = f"{last_seq + 1:03d}"  
        else:
            new_seq = "001"  
        loan_accno = f"{today}{new_seq}" 
        
        customer_data= validated_data.pop('customer', {})
        
        customer, created = Customer.objects.get_or_create(**customer_data)
        loan = Loan.objects.create(loan_accno=loan_accno, customer=customer, **validated_data)

        due_date = loan.next_payment_date
        frequency_map = {"Monthly": 30, "Weekly": 7, "Daily": 1}
        interval = timedelta(days=frequency_map.get(loan.payment_frequency, 30))

        for seq in range(1, loan.term + 1):
            LoanBill.objects.create(
                loan_acc=loan,
                bill_seq=seq,
                bill_date=due_date,
                total_due=loan.emi_amount,
                payment_status="Pending"
            )
            due_date += interval  

        return loan
    
    
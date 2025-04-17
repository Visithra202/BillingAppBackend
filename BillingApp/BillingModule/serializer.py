from rest_framework import serializers
from .models import *
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.timezone import now
from datetime import timedelta
from datetime import datetime
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from decimal import Decimal


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
        fields = ['item_id', 'item_name', 'category', 'brand', 'quantity', 'min_stock', 'purchase_price', 'sale_price', 'tax_option', 'mrp', 'discount_type', 'discount']

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
    product = ItemSerializer()

    class Meta:
        model = SaleItem  # Dummy model for inheritance
        fields = ['product', 'item_seq', 'quantity', 'unit_price', 'total_price']

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
    sale_products = SaleItemSerializer(source='sale_items', many=True)
    payment = PaymentSerializer()
    customer = CustomerSerializer()

    class Meta:
        model = Sale
        fields = ['bill_no', 'sale_date', 'customer', 'payment', 'total_amount', 'discount', 'sale_products', 'balance']

    @transaction.atomic
    def create(self, validated_data):
        customer_data = validated_data.pop('customer')
        payment_data = validated_data.pop('payment')
        sale_items_data = validated_data.pop('sale_items', [])

        customer, _ = Customer.objects.get_or_create(**customer_data)

        payment = Payment.objects.create(**payment_data)

        current_year = datetime.now().year
        bill, created = SaleBill.objects.get_or_create(
            bill_year=current_year,
            defaults={'bill_seq': 1}
        )
        if not created:
            bill.bill_seq += 1
            bill.save()

        validated_data['bill_no'] = f'BILL-{current_year}-{bill.bill_seq:02d}'

        sale = Sale.objects.create(
            customer=customer,
            payment=payment,
            sale_seq=bill.bill_seq - 1,
            **validated_data
        )

        for index, item_data in enumerate(sale_items_data):
            product_data = item_data.pop("product")

            try:
                item = Item.objects.get(
                    item_name=product_data['item_name'],
                    category=product_data['category'],
                    brand=product_data['brand'],
                    sale_price=product_data['sale_price']
                )

                if item.quantity >= item_data['quantity']:
                    item.quantity -= item_data['quantity']
                    item.save()

                    SaleItem.objects.create(
                        sale=sale,
                        item_seq=index + 1,
                        product=item,
                        **item_data
                    )
                else:
                    raise serializers.ValidationError(f"Not enough stock for {item.item_name}")

            except ObjectDoesNotExist:
                raise serializers.ValidationError(f"Item '{product_data['item_name']}' not found.")

        return sale

class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = '__all__'

class PurchaseSerializer(serializers.ModelSerializer):
    purchase_products = PurchaseItemSerializer(source='purchase_items', many=True)
    purchase_payment = PurchasePaymentSerializer()
    seller = SellerSerializer()

    class Meta:
        model = Purchase
        fields = ['purchase_id', 'purchase_date', 'seller', 'purchase_payment', 'total_amount', 'discount', 'purchase_products', 'balance']

    @transaction.atomic
    def create(self, validated_data):
        seller_data = validated_data.pop('seller')
        payment_data = validated_data.pop('purchase_payment')
        purchase_items_data = validated_data.pop('purchase_items', [])

        seller, _ = Seller.objects.get_or_create(**seller_data)

        payment = PurchasePayment.objects.create(**payment_data)

        current_year = datetime.now().year
        bill, created = PurchaseBill.objects.get_or_create(
            bill_year=current_year,
            defaults={'bill_seq': 1}
        )
        if not created:
            bill.bill_seq += 1
            bill.save()

        validated_data['purchase_id'] = f'PUR-{current_year}-{bill.bill_seq:02d}'

        purchase = Purchase.objects.create(
            seller=seller,
            purchase_payment=payment,
            purchase_seq=bill.bill_seq - 1,
            **validated_data
        )

        for index, item_data in enumerate(purchase_items_data):
            product_data = item_data.pop("product")

            try:
                item = Item.objects.get(
                    item_name=product_data['item_name'],
                    category=product_data['category'],
                    brand=product_data['brand'],
                    sale_price=product_data['sale_price']
                )

                item.quantity += item_data['quantity']
                item.save()

                PurchaseItem.objects.create(
                    purchase=purchase,
                    item_seq=index + 1,
                    product=item,
                    **item_data
                )

            except ObjectDoesNotExist:
                raise serializers.ValidationError(f"Item '{product_data['item_name']}' not found.")

        return purchase

class LoanSerializer(serializers.ModelSerializer):
    customer= CustomerSerializer()
    
    class Meta:
        model = Loan
        fields = '__all__'
        read_only_fields = ['loan_accno']  

    @transaction.atomic
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

        due_date = loan.next_pay_date
        frequency_map = {"Monthly": 30, "Weekly": 7}
        interval = timedelta(days=frequency_map.get(loan.payment_freq, 30))

        if loan.payment_freq == "Weekly":
            total_bills = loan.term * 4 
        else:
            total_bills = loan.term

        for seq in range(1, total_bills + 1):
            LoanBill.objects.create(
                loan_acc=loan,
                bill_seq=seq,
                bill_date=due_date,
                due_amount=loan.emi_amount,
                total_due=loan.emi_amount,
            )
            due_date += interval
        
        # latest_journal_entry = LoanJournal.objects.last() 

        # if latest_journal_entry:
        #     previous_balance = latest_journal_entry.balance_amount
        # else:
        #     previous_balance = Decimal('0.00')
            
            
        journal_entry = LoanJournal.objects.create(
            loan=loan,
            journal_date=today,
            action_type='CREATE',
            description="Loan account creation",
            new_data=Decimal(loan.loan_amount),
            debit=True,
            trans_amt=Decimal(loan.loan_amount),
            balance_amount=Decimal(loan.loan_amount)
        )
        return loan
    
class GlHistSerializer(serializers.ModelSerializer):

    class Meta:
        model = GlHist
        fields = '__all__'

class LoanJournalSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanJournal
        fields = '__all__'
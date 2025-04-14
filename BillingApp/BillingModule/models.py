from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.timezone import now
from datetime import date


class Compdet(models.Model):
    logo_path=models.TextField(max_length=200)

class Category(models.Model):
    category_id=models.AutoField(primary_key=True)
    category_name=models.CharField(max_length=255)
    description=models.TextField()

    def __str__(self):
        return self.category_name
    
class Brand(models.Model):
    brand_id=models.AutoField(primary_key=True)
    brand_name=models.CharField(max_length=255)
    description=models.TextField()
    
    def __str__(self):
        return self.brand_name


class Item(models.Model):
    item_id=models.AutoField(primary_key=True)
    item_name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    brand = models.CharField(max_length=255)
    quantity = models.IntegerField()
    min_stock = models.IntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    tax_option=models.CharField(max_length=50, null=True, blank=True)
    mrp = models.DecimalField(max_digits=10, decimal_places=2)
    discount_type=models.CharField(max_length=50, null=True, blank=True)
    discount=models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    
    def __str__(self):
        return self.item_name

class Customer(models.Model):
    customer_id =models.AutoField(primary_key=True)
    customer_name=models.CharField(max_length=255)
    mph=PhoneNumberField(region="IN")
    address=models.TextField()
    
    def __str__(self):
        return self.customer_name

class SaleBill(models.Model):
    bill_year=models.IntegerField(primary_key=True)
    bill_seq=models.IntegerField(default=1)

class PurchaseBill(models.Model):
    bill_year=models.IntegerField(primary_key=True)
    bill_seq=models.IntegerField(default=1)


class Payment(models.Model):
    payment_id=models.AutoField(primary_key=True)
    cash = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    account = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Payment - Cash: {self.cash}, Account: {self.account}, Credit: {self.credit}"
    
class PurchasePayment(models.Model):
    payment_id=models.AutoField(primary_key=True)
    cash = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    account = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    

class Sale(models.Model):
    bill_no = models.CharField(primary_key=True, max_length=15)
    sale_seq=models.IntegerField(default=1)
    sale_date = models.DateField(default=date.today)
    customer = models.ForeignKey("Customer", on_delete=models.CASCADE, null=True, blank=True)
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sale_products = models.ManyToManyField("Item", through="SaleItem")

    def __str__(self):
        return f"Sale {self.bill_no} - Total: {self.total_amount}"


class Purchase(models.Model):
    purchase_id = models.CharField(primary_key=True, max_length=15)
    purchase_seq=models.IntegerField(default=1)
    purchase_date = models.DateField(default=date.today)
    seller = models.ForeignKey("Seller", on_delete=models.CASCADE)
    purchase_payment = models.OneToOneField(PurchasePayment, on_delete=models.CASCADE, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    purchase_products = models.ManyToManyField("Item", through="PurchaseItem")
    
    def __str__(self):
        return f"Purchase {self.purchase_id} - Total: {self.total_amount}"


class TransactionItem(models.Model):
    item_seq = models.IntegerField(default=1)
    product = models.ForeignKey("Item", on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        abstract = True  # This makes the model an abstract base class

class SaleItem(TransactionItem):
    sale = models.ForeignKey("Sale", on_delete=models.CASCADE, related_name="sale_items")

    def __str__(self):
        return f"Sale {self.sale.id} - {self.product.item_name} ({self.quantity})"

class PurchaseItem(TransactionItem):
    purchase = models.ForeignKey("Purchase", on_delete=models.CASCADE, related_name="purchase_items")

    def __str__(self):
        return f"Purchase {self.purchase.id} - {self.product.item_name} ({self.quantity})"


class Loan(models.Model):
    loan_accno=models.CharField(primary_key=True, max_length=15)
    customer=models.ForeignKey('Customer', on_delete=models.CASCADE)
    loan_amount=models.DecimalField(max_digits=10, decimal_places=2)
    payment_amount=models.DecimalField(max_digits=10, decimal_places=2)
    emi_amount=models.DecimalField(max_digits=10, decimal_places=2)
    term=models.IntegerField()
    payment_freq=models.CharField(max_length=15)
    interest=models.DecimalField(max_digits=10, decimal_places=2)
    loan_date=models.DateField(default=date.today)
    next_pay_date=models.DateField()
    bal_amount=models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return self.loan_accno
    
    
class LoanBill(models.Model):
    loan_acc=models.ForeignKey('Loan', on_delete=models.CASCADE)
    bill_seq=models.IntegerField()
    bill_date=models.DateField()
    paid_date=models.DateField(null=True, blank=True)
    due_amount=models.DecimalField(max_digits=10, decimal_places=2)
    late_fee=models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_due=models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount=models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
class Seller(models.Model):
    seller_id=models.AutoField(primary_key=True)
    seller_name=models.CharField(max_length=255)
    seller_mph=PhoneNumberField(region='IN')
    address=models.TextField()
    
    def __str__(self):
        return self.seller_name


class LoanJournal(models.Model):
    journal_id=models.AutoField(primary_key=True)
    ACTION_CHOICES = [('CREATED', 'Loan Issued'), ('PAYMENT', 'Payment Made'),('UPDATED', 'Loan Updated'),('CLOSED', 'Loan Closed')]
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='journal_entries')
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField()
    old_data = models.JSONField(null=True, blank=True)
    new_data = models.JSONField(null=True, blank=True)
    credit=models.DecimalField(max_digits=10, decimal_places=2)
    debit=models.DecimalField(max_digits=10, decimal_places=2)
    balance_amount=models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.action_type} for Loan #{self.journal_id}"

class GlHist(models.Model):
    trans_seq=models.AutoField(primary_key=True)
    date= models.DateField(default=now)
    loan_acc=models.ForeignKey(Loan, on_delete=models.CASCADE)
    trans_command=models.TextField()
    credit=models.BooleanField(default=False)
    debit=models.BooleanField(default=False)
    trans_amount=models.DecimalField(max_digits=10, decimal_places=2)
    balance=models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.loan_acc}"


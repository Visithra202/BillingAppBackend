from datetime import datetime
from django.db.models import F
from BillingModule.models import LoanBill  # Replace `your_app_name` with your Django app name

        
import schedule
import threading
import time
from datetime import date

def start_task():
    schedule.every().day.at("12:15").do(apply_task)
    
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(1)

    scheduler_threading = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_threading.start()

def apply_task():
    today = date.today()
    bills = LoanBill.objects.all()

    for bill in bills:
        if (bill.bill_date and bill.bill_date < today and not bill.paid_date):
            print(f"Late bill found: {bill.loan_acc} | Due: {bill.bill_date}")
            bill.late_fee += 100
            bill.total_due=bill.due_amount+bill.late_fee
            bill.save()
        
if __name__ == '__main__':
    start_task()
    while True:
        time.sleep(1)
        
# execution in shell
from BillingModule.models import LoanBill
from BillingModule.latefeeupd import start_task
start_task()
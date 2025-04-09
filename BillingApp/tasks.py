import os
import django
import sys
import time
import schedule
import threading

sys.path.append(os.path.abspath('D:/Github/BillingAppBackend'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BillingApp.BillingApp.settings')
django.setup()

from BillingApp.BillingModule.models import *

def start_task():
    schedule.every(1).seconds.do(run_task)

    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(1)

    scheduler_threading = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_threading.start()

def run_task():
    print('hello')
    
# def apply_task():
#     bill = Bill.objects.all().first()
#     if bill:
#         print(bill.bill_seq + ' ' + bill.bill_year)
#     else:
#         print("No bills found.")

if __name__ == '__main__':
    start_task()
    while True:
        time.sleep(1)

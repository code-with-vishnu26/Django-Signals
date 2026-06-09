import time
import threading
from django.core.management.base import BaseCommand
from django.db import transaction
from signals_app.models import TestModel, Order, Log
from signals_app.signals import execution_log
from rectangle import Rectangle


class Command(BaseCommand):
    help = 'Executes proofs demonstrating Django Signal properties and the custom Rectangle class.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("\n=================================================="))
        self.stdout.write(self.style.NOTICE("        ACCUKNOX ASSIGNMENT: SIGNAL PROOFS        "))
        self.stdout.write(self.style.NOTICE("==================================================\n"))

        # Clear DB before run
        TestModel.objects.all().delete()
        Order.objects.all().delete()
        Log.objects.all().delete()

        # --- Q1: Are Django signals synchronous by default? ---
        self.stdout.write(self.style.WARNING("Question 1: Are Django signals synchronous or asynchronous by default?"))
        self.stdout.write("Hypothesis: If synchronous, save operations will block during signal execution.")
        
        start_time = time.time()
        self.stdout.write("--> Saving TestModel 'sleep_test_cli' (triggers 5-second sleep in receiver)...")
        TestModel.objects.create(name="sleep_test_cli")
        end_time = time.time()
        duration = end_time - start_time
        
        self.stdout.write(self.style.SUCCESS(f"--> Save operation completed in {duration:.4f} seconds."))
        if duration >= 5.0:
            self.stdout.write(self.style.SUCCESS("Conclusion: The caller execution was blocked for >= 5 seconds. Django signals are SYNCHRONOUS by default.\n"))
        else:
            self.stdout.write(self.style.ERROR("Conclusion: Save took less than 5 seconds. Signals are ASYNCHRONOUS.\n"))

        # --- Q2: Do signals run in the same thread? ---
        self.stdout.write(self.style.WARNING("Question 2: Do Django signals run in the same thread as the caller?"))
        caller_tid = threading.current_thread().ident
        caller_tname = threading.current_thread().name
        self.stdout.write(f"--> Caller Thread Name: {caller_tname} (ID: {caller_tid})")

        execution_log['signal_thread_id'] = None
        TestModel.objects.create(name="thread_test_cli")
        
        signal_tid = execution_log['signal_thread_id']
        signal_tname = execution_log['signal_thread_name']
        self.stdout.write(f"--> Signal Thread Name: {signal_tname} (ID: {signal_tid})")

        if caller_tid == signal_tid:
            self.stdout.write(self.style.SUCCESS(f"Conclusion: Thread IDs are identical ({caller_tid}). Signals run in the SAME THREAD as the caller.\n"))
        else:
            self.stdout.write(self.style.ERROR("Conclusion: Thread IDs differ. Signals run in a DIFFERENT THREAD.\n"))

        # --- Q3: Do signals run in the same database transaction? ---
        self.stdout.write(self.style.WARNING("Question 3: Do Django signals run in the same database transaction as the caller?"))
        self.stdout.write("Hypothesis: If in the same transaction, rolling back the caller transaction rolls back the signal's DB modifications.")
        self.stdout.write(f"--> Initial counts - Orders: {Order.objects.count()}, Logs: {Log.objects.count()}")

        try:
            with transaction.atomic():
                self.stdout.write("--> Creating Order 'Laptop' inside transaction.atomic()...")
                Order.objects.create(name="Laptop")
                self.stdout.write(f"--> Inside transaction - Orders: {Order.objects.count()}, Logs: {Log.objects.count()} (created by signal)")
                self.stdout.write("--> Raising forced exception to trigger rollback...")
                raise Exception("Forced Rollback")
        except Exception:
            self.stdout.write("--> Transaction Exception caught and handled.")

        final_orders = Order.objects.count()
        final_logs = Log.objects.count()
        self.stdout.write(f"--> Post-rollback counts - Orders: {final_orders}, Logs: {final_logs}")

        if final_orders == 0 and final_logs == 0:
            self.stdout.write(self.style.SUCCESS("Conclusion: The Log record created by the signal receiver was rolled back. Signals execute in the SAME TRANSACTION.\n"))
        else:
            self.stdout.write(self.style.ERROR("Conclusion: Log record persisted. Signals execute in a SEPARATE TRANSACTION.\n"))

        # --- Custom Rectangle Class ---
        self.stdout.write(self.style.NOTICE("=================================================="))
        self.stdout.write(self.style.NOTICE("           PYTHON CUSTOM CLASS: RECTANGLE         "))
        self.stdout.write(self.style.NOTICE("==================================================\n"))
        self.stdout.write("Initializing Rectangle(10, 5) and iterating:")
        
        rect = Rectangle(10, 5)
        for item in rect:
            self.stdout.write(f"--> Iterated item: {item}")
        self.stdout.write(self.style.SUCCESS("\nAll proofs executed successfully!"))

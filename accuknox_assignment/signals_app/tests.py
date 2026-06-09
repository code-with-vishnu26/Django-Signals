import time
import threading
from django.test import TestCase
from django.db import transaction
from .models import TestModel, Order, Log
from .signals import execution_log
from rectangle import Rectangle


class DjangoSignalsTest(TestCase):
    """
    Test suite verifying Django Signal behavior regarding
    synchronicity, threading, and database transaction scope.
    """

    def test_question_1_synchronous_execution(self):
        """
        Proof Q1: Verify that Django signals execute synchronously by default.
        By saving a TestModel instance with 'sleep_test' name, the receiver
        sleeps for 5 seconds. If synchronous, the caller's execution will block,
        making the elapsed time >= 5.0 seconds.
        """
        start_time = time.time()
        TestModel.objects.create(name="sleep_test_verification")
        end_time = time.time()
        elapsed_time = end_time - start_time

        print(f"\n[Test Q1] Signal duration: {elapsed_time:.4f}s")
        self.assertGreaterEqual(elapsed_time, 5.0)

    def test_question_2_same_thread(self):
        """
        Proof Q2: Verify that Django signals run in the same thread as the caller.
        We capture the current thread ID in the test (caller) and compare it
        with the thread ID captured inside the signal handler.
        """
        caller_thread_id = threading.current_thread().ident
        
        # Reset execution log
        execution_log['signal_thread_id'] = None

        # Triggers post_save signal
        TestModel.objects.create(name="thread_test_verification")

        signal_thread_id = execution_log['signal_thread_id']
        
        print(f"\n[Test Q2] Caller thread ID: {caller_thread_id}, Signal thread ID: {signal_thread_id}")
        self.assertIsNotNone(signal_thread_id)
        self.assertEqual(caller_thread_id, signal_thread_id)

    def test_question_3_same_transaction_scope(self):
        """
        Proof Q3: Verify that Django signals run in the same database transaction.
        We run inside an atomic block, create an Order (which creates a Log record in the signal),
        then raise an Exception to rollback. Both Order and Log must disappear.
        """
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(Log.objects.count(), 0)

        try:
            with transaction.atomic():
                # Order creation triggers signal handler which creates a Log
                Order.objects.create(name="Laptop")
                
                # Check counts inside the transaction context
                self.assertEqual(Order.objects.count(), 1)
                self.assertEqual(Log.objects.count(), 1)
                
                raise Exception("Rollback transaction")
        except Exception:
            pass

        # Since transaction was rolled back, counts should go back to 0
        print(f"\n[Test Q3] Post-rollback Counts - Orders: {Order.objects.count()}, Logs: {Log.objects.count()}")
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(Log.objects.count(), 0)


class RectangleClassTest(TestCase):
    """
    Test suite verifying the custom iterable Rectangle class behavior.
    """

    def test_rectangle_iteration(self):
        """
        Verify that a Rectangle instance yields its length first, then width,
        formatted as dictionaries.
        """
        rect = Rectangle(10, 5)
        result = list(rect)

        print(f"\n[Test Rectangle] Result: {result}")
        self.assertEqual(result, [
            {"length": 10},
            {"width": 5}
        ])

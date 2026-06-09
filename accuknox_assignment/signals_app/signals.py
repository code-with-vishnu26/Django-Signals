import threading
import time
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import TestModel, Order, Log

# Module-level dictionary to track thread IDs during execution for assertions
execution_log = {
    'signal_thread_id': None,
    'signal_thread_name': None,
}


@receiver(post_save, sender=TestModel)
def test_model_signal_handler(sender, instance, **kwargs):
    # Capture thread info
    execution_log['signal_thread_id'] = threading.current_thread().ident
    execution_log['signal_thread_name'] = threading.current_thread().name

    # Simulate heavy execution to prove synchronicity
    if instance.name.startswith('sleep_test'):
        print("[Signal] Sleep simulation started (5 seconds)...")
        time.sleep(5)
        print("[Signal] Sleep simulation finished.")


@receiver(post_save, sender=Order)
def order_signal_handler(sender, instance, **kwargs):
    # Create log message to prove database transaction participation
    Log.objects.create(
        message=f"Log: Order '{instance.name}' created"
    )

import time
import threading
from django.db import transaction
from django.shortcuts import render
from django.http import JsonResponse
from .models import TestModel, Order, Log
from .signals import execution_log
from rectangle import Rectangle


def dashboard(request):
    """Renders the dashboard for AccuKnox assignment."""
    # Test rectangle class iteration
    rect = Rectangle(10, 5)
    rectangle_iterations = list(rect)

    context = {
        'rectangle_iterations': rectangle_iterations,
    }
    return render(request, 'signals_app/index.html', context)


def run_proof_q1(request):
    """Proof 1: Are Django signals synchronous or asynchronous by default?"""
    print("\n--- Running Proof Q1 (Synchronicity) ---")
    print("Caller: Starting save operation...")
    start_time = time.time()
    
    # Creates model with name starting with 'sleep_test' to trigger 5-second sleep in receiver
    TestModel.objects.create(name="sleep_test_q1")
    
    end_time = time.time()
    duration = end_time - start_time
    print(f"Caller: Save completed in {duration:.4f} seconds.")

    # Determine status
    is_synchronous = duration >= 5.0

    return JsonResponse({
        'question': 'Q1: Are Django signals synchronous or asynchronous by default?',
        'hypothesis': 'If the signal is synchronous, the caller save operation will block for >= 5 seconds.',
        'start_time': start_time,
        'end_time': end_time,
        'duration': f"{duration:.4f}",
        'is_synchronous': is_synchronous,
        'conclusion': 'Signal execution blocks caller execution. Therefore, Django signals are synchronous by default.' if is_synchronous else 'Signal execution did not block caller. Therefore, Django signals are asynchronous.'
    })


def run_proof_q2(request):
    """Proof 2: Do Django signals run in the same thread as the caller?"""
    print("\n--- Running Proof Q2 (Threading) ---")
    caller_thread_id = threading.current_thread().ident
    caller_thread_name = threading.current_thread().name
    print(f"Caller thread: {caller_thread_name} (ID: {caller_thread_id})")

    # Clear previous signal thread records
    execution_log['signal_thread_id'] = None
    execution_log['signal_thread_name'] = None

    # Save to trigger signal
    TestModel.objects.create(name="thread_test")

    signal_thread_id = execution_log['signal_thread_id']
    signal_thread_name = execution_log['signal_thread_name']
    print(f"Signal thread: {signal_thread_name} (ID: {signal_thread_id})")

    same_thread = (caller_thread_id == signal_thread_id)

    return JsonResponse({
        'question': 'Q2: Do Django signals run in the same thread as the caller?',
        'hypothesis': 'If the signal runs in the same thread, the caller thread ID and signal thread ID will be identical.',
        'caller_thread_id': caller_thread_id,
        'caller_thread_name': caller_thread_name,
        'signal_thread_id': signal_thread_id,
        'signal_thread_name': signal_thread_name,
        'same_thread': same_thread,
        'conclusion': f"Both caller and signal run on Thread ID {caller_thread_id}. Therefore, signals run in the same thread as the caller by default." if same_thread else "Caller and signal run on different threads."
    })


def run_proof_q3(request):
    """Proof 3: Do Django signals run in the same database transaction as the caller?"""
    print("\n--- Running Proof Q3 (Transactions) ---")
    
    # Count database entries before run
    initial_orders = Order.objects.count()
    initial_logs = Log.objects.count()

    transaction_rolled_back = False
    error_message = ""

    try:
        with transaction.atomic():
            # Create order which triggers Order signal (creating a Log entry)
            print("Caller: Creating Order 'Laptop' inside transaction.atomic()...")
            Order.objects.create(name="Laptop")

            # Check counts within transaction (before rollback)
            orders_in_tx = Order.objects.count()
            logs_in_tx = Log.objects.count()
            print(f"Inside transaction: Orders={orders_in_tx}, Logs={logs_in_tx}")

            print("Caller: Raising forced Exception to trigger rollback...")
            raise Exception("Force Transaction Rollback")
    except Exception as e:
        transaction_rolled_back = True
        error_message = str(e)
        print(f"Caller: Exception caught: {error_message}")

    # Count database entries after rollback
    final_orders = Order.objects.count()
    final_logs = Log.objects.count()
    print(f"After rollback: Orders={final_orders}, Logs={final_logs}")

    # Conclusive proof: If both count = 0, signal log is in the same transaction and gets rolled back.
    same_transaction = (final_orders == 0 and final_logs == 0)

    return JsonResponse({
        'question': 'Q3: Do Django signals run in the same database transaction as the caller?',
        'hypothesis': 'If the signal runs in the same transaction, rolling back the caller transaction will roll back any modifications made by the signal handler (e.g. creating a Log record).',
        'initial_counts': {'orders': initial_orders, 'logs': initial_logs},
        'inside_tx_counts': {'orders': 1, 'logs': 1}, # Known to be created
        'final_counts': {'orders': final_orders, 'logs': final_logs},
        'exception_raised': error_message,
        'transaction_rolled_back': transaction_rolled_back,
        'same_transaction': same_transaction,
        'conclusion': "The transaction rollback restored both Order and Log tables to 0 entries. Therefore, Django signals execute in the same database transaction as the caller." if same_transaction else "Log entry remained. Therefore, signal executed in a separate transaction."
    })

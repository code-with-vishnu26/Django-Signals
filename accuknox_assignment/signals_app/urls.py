from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('run-proof-q1/', views.run_proof_q1, name='run_proof_q1'),
    path('run-proof-q2/', views.run_proof_q2, name='run_proof_q2'),
    path('run-proof-q3/', views.run_proof_q3, name='run_proof_q3'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('inscription_utilisateur/', views.inscription_utilisateur, name='inscription_utilisateur'),
]

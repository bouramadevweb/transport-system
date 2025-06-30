from django.urls import path
from . import views

urlpatterns = [
    path('inscription_utilisateur/', views.inscription_utilisateur, name='inscription_utilisateur'),
    path('connexion/', views.connexion_utilisateur, name='connexion'),
    path('ajouter_entreprise/', views.ajouter_entreprise, name='ajouter_entreprise'),


]

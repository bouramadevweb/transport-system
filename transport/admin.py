from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Entreprise, Utilisateur,Chauffeur, Camion, Affectation, Transitaire, Client, CompagnieConteneur, Conteneur, ContratTransport, PrestationDeTransports,Cautions, FraisTrajet,Mission,MissionConteneur,PaiementMission,Mecanicien,Fournisseur,Reparation,ReparationMecanicien,PieceReparee
#from .forms import CustomUserCreationForm

# Register your models here.
admin.site.register(Entreprise)

@admin.register(Utilisateur)
class CustomUserAdmin(UserAdmin):
    model = Utilisateur
    list_display = ('email', 'role', 'actif', 'entreprise', 'date_creation')
    list_filter = ('role', 'actif', 'entreprise')
    ordering = ('email',)
    search_fields = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password', 'entreprise')}),
        ('Permissions', {'fields': ('role', 'is_staff', 'is_superuser', 'actif')}),
        ('Dates', {'fields': ('date_creation',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'entreprise', 'password1', 'password2', 'role', 'actif')}
        ),
    )
admin.site.register(Chauffeur)
admin.site.register(Camion)
admin.site.register(Affectation)
admin.site.register(Transitaire)
admin.site.register(Client)
admin.site.register(CompagnieConteneur)
admin.site.register(Conteneur)
admin.site.register(ContratTransport)
admin.site.register(PrestationDeTransports)
admin.site.register(Cautions)
admin.site.register(FraisTrajet)
admin.site.register(Mission)
admin.site.register(MissionConteneur)
admin.site.register(PaiementMission)
admin.site.register(Mecanicien)
admin.site.register(Fournisseur)
admin.site.register(Reparation)
admin.site.register(ReparationMecanicien)
admin.site.register(PieceReparee)
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Entreprise, Utilisateur,Chauffeur, Camion, Affectation, Transitaire, Client, CompagnieConteneur, Conteneur, ContratTransport, PrestationDeTransports,Cautions, FraisTrajet,Mission,MissionConteneur,PaiementMission,Mecanicien,Fournisseur,Reparation,ReparationMecanicien,PieceReparee




@admin.register(Entreprise)
class EntrepriseAdmin(admin.ModelAdmin):
    list_display = (
        'pk_entreprise',
        'nom',
        'secteur_activite',
        'email_contact',
        'telephone_contact',
        'date_creation',
        'statut',
    )
    search_fields = ('nom', 'secteur_activite', 'email_contact')
    list_filter = ('statut', 'date_creation')
    ordering = ('-date_creation',)
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
@admin.register(Chauffeur)
class ChauffeurAdmin(admin.ModelAdmin):
    list_display = ('pk_chauffeur', 'nom', 'prenom', 'email', 'telephone', 'entreprise')
    search_fields = ('nom', 'prenom', 'email')
    list_filter = ('entreprise',)
    ordering = ('nom', 'prenom')

@admin.register(Camion)
class CamionAdmin(admin.ModelAdmin):
    list_display = ('pk_camion', 'entreprise', 'immatriculation', 'modele', 'capacite_tonnes')
    search_fields = ('immatriculation', 'modele')
    list_filter = ('entreprise',)
    ordering = ('immatriculation',)

#admin.site.register(Affectation)
@admin.register(Affectation)
class AffectationAdmin(admin.ModelAdmin):
    list_display = ('pk_affectation', 'chauffeur', 'camion', 'date_affectation', 'date_fin_affectation')
    list_filter = ('chauffeur', 'camion', 'date_affectation')
    search_fields = ('pk_affectation', 'chauffeur__nom', 'camion__immatriculation')
    ordering = ('-date_affectation',)

@admin.register(Transitaire)
class TransitaireAdmin(admin.ModelAdmin):
    list_display = (
        'pk_transitaire', 'nom', 'telephone', 'email',
        'score_fidelite', 'etat_paiement'
    )
    search_fields = ('nom', 'telephone', 'email')
    list_filter = ('etat_paiement',)
    ordering = ('nom',)

#admin.site.register(Client)
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = (
        'pk_client', 'nom', 'type_client', 'telephone',
        'email', 'score_fidelite', 'etat_paiement'
    )
    search_fields = ('nom', 'telephone', 'email')
    list_filter = ('type_client', 'etat_paiement')
    ordering = ('nom',)

#admin.site.register(CompagnieConteneur)
@admin.register(CompagnieConteneur)
class CompagnieConteneurAdmin(admin.ModelAdmin):
    list_display = ('pk_compagnie', 'nom')
    search_fields = ('nom',)
    ordering = ('nom',)

#admin.site.register(Conteneur)
@admin.register(Conteneur)
class ConteneurAdmin(admin.ModelAdmin):
    list_display = (
        'pk_conteneur',
        'numero_conteneur',
        'compagnie',
        'type_conteneur',
        'poids',
        'client',
        'transitaire',
    )
    search_fields = ('numero_conteneur', 'client__nom', 'compagnie__nom')
    list_filter = ('compagnie', 'client', 'transitaire')
    ordering = ('numero_conteneur',)

@admin.register(ContratTransport)
class ContratTransportAdmin(admin.ModelAdmin):
    list_display = (
        'pk_contrat', 'conteneur', 'client', 'transitaire',
        'entreprise', 'camion', 'chauffeur',
        'date_debut', 'date_limite_retour',
        'caution', 'statut_caution',
        'signature_chauffeur', 'signature_client', 'signature_transitaire',
    )
    list_filter = (
        'statut_caution', 'signature_chauffeur', 'signature_client',
        'signature_transitaire', 'entreprise',
    )
    search_fields = (
        'pk_contrat', 'conteneur__numero_conteneur',
        'client__nom', 'transitaire__nom',
        'camion__immatriculation', 'chauffeur__nom',
    )
    date_hierarchy = 'date_debut'

#admin.site.register(PrestationDeTransports)
@admin.register(PrestationDeTransports)
class PrestationDeTransportsAdmin(admin.ModelAdmin):
    list_display = (
        'pk_presta_transport',
        'contrat_transport',
        'camion',
        'client',
        'transitaire',
        'prix_transport',
        'avance',
        'caution',
        'solde',
        'date',
    )
    list_filter = (
        'date',
        'client',
        'transitaire',
    )
    search_fields = (
        'pk_presta_transport',
        'contrat_transport__pk_contrat',
        'camion__immatriculation',
        'client__nom',
        'transitaire__nom',
    )
    date_hierarchy = 'date'
#admin.site.register(Cautions)
@admin.register(Cautions)
class CautionsAdmin(admin.ModelAdmin):
    list_display = (
        'pk_caution',
        'conteneur',
        'contrat',
        'transitaire',
        'client',
        'chauffeur',
        'camion',
        'montant',
        'statut',
        'montant_rembourser',
    )
    list_filter = (
        'statut',
        'transitaire',
        'client',
    )
    search_fields = (
        'pk_caution',
        'conteneur__numero_conteneur',
        'contrat__pk_contrat',
        'client__nom',
        'transitaire__nom',
        'chauffeur__nom',
        'camion__immatriculation',
    )
#admin.site.register(FraisTrajet)
@admin.register(FraisTrajet)
class FraisTrajetAdmin(admin.ModelAdmin):
    list_display = ('pk_frais', 'get_mission_short', 'get_camion', 'get_chauffeur', 'type_trajet', 'date_trajet', 'origine', 'destination', 'get_total')
    search_fields = ('^pk_frais', '^contrat__numero_bl', 'origine', 'destination', '^contrat__camion__immatriculation')
    list_filter = ('type_trajet', 'date_trajet', 'origine', 'destination')
    autocomplete_fields = ('mission', 'contrat')

    def get_mission_short(self, obj):
        """Affiche les 20 premiers caractères de la mission"""
        if obj.mission:
            return f"{obj.mission.pk_mission[:20]}..."
        return "—"
    get_mission_short.short_description = 'Mission'

    def get_camion(self, obj):
        """Affiche l'immatriculation du camion"""
        if obj.contrat and obj.contrat.camion:
            return obj.contrat.camion.immatriculation
        return "—"
    get_camion.short_description = 'Camion'

    def get_chauffeur(self, obj):
        """Affiche le nom du chauffeur"""
        if obj.contrat and obj.contrat.chauffeur:
            return f"{obj.contrat.chauffeur.nom} {obj.contrat.chauffeur.prenom}"
        return "—"
    get_chauffeur.short_description = 'Chauffeur'

    def get_total(self, obj):
        """Affiche le total des frais"""
        return f"{obj.total_frais} FCFA"
    get_total.short_description = 'Total'

#admin.site.register(Mission)
@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = (
        'pk_mission', 'prestation_transport', 'date_depart', 'date_retour',
        'origine', 'destination', 'contrat', 'statut'
    )
    search_fields = ('pk_mission', 'origine', 'destination', 'contrat__pk_contrat')
    list_filter = ('statut', 'origine', 'destination', 'date_depart')
    autocomplete_fields = ('prestation_transport', 'contrat')

#admin.site.register(MissionConteneur)
@admin.register(MissionConteneur)
class MissionConteneurAdmin(admin.ModelAdmin):
    list_display = ('mission', 'conteneur')
    search_fields = ('mission__pk_mission', 'conteneur__pk_conteneur')
    list_filter = ('mission', 'conteneur')
    autocomplete_fields = ('mission', 'conteneur')

#admin.site.register(PaiementMission)
@admin.register(PaiementMission)
class PaiementMissionAdmin(admin.ModelAdmin):
    list_display = (
        'pk_paiement', 'mission', 'prestation', 'caution',
        'montant_total', 'commission_transitaire',
        'caution_est_retiree', 'date_paiement'
    )
    search_fields = ('pk_paiement', 'mission__pk_mission', 'prestation__pk_presta_transport')
    list_filter = ('caution_est_retiree', 'date_paiement', 'mode_paiement')
    autocomplete_fields = ('mission', 'prestation', 'caution')

@admin.register(Mecanicien)
class MecanicienAdmin(admin.ModelAdmin):
    list_display = ('pk_mecanicien', 'nom', 'telephone', 'email', 'created_at', 'updated_at')
    search_fields = ('nom', 'telephone', 'email')

@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    list_display = ('pk_fournisseur', 'nom', 'telephone', 'email', 'fiabilite', 'created_at')
    search_fields = ('nom', 'telephone', 'email')
    list_filter = ('fiabilite',)

@admin.register(Reparation)
class ReparationAdmin(admin.ModelAdmin):
    list_display = ('pk_reparation', 'camion', 'chauffeur', 'date_reparation', 'cout')
    search_fields = ('pk_reparation', 'camion__immatriculation', 'chauffeur__nom')
    list_filter = ('date_reparation',)

@admin.register(ReparationMecanicien)
class ReparationMecanicienAdmin(admin.ModelAdmin):
    list_display = ('reparation', 'mecanicien')
    autocomplete_fields = ('reparation', 'mecanicien')

@admin.register(PieceReparee)
class PieceRepareeAdmin(admin.ModelAdmin):
    list_display = ('pk_piece', 'nom_piece', 'categorie', 'quantite', 'cout_unitaire', 'fournisseur', 'reparation')
    list_filter = ('categorie', 'fournisseur')
    search_fields = ('nom_piece', 'reference', 'pk_piece')
    autocomplete_fields = ('reparation', 'fournisseur')
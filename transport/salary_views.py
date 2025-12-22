"""
Vues pour la gestion des salaires
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from transport.models import Salaire, Prime, Deduction, Chauffeur, Utilisateur
from transport.permissions import role_required
from datetime import datetime
from decimal import Decimal


@login_required
@role_required('ADMIN', 'COMPTABLE')
def salaire_list(request):
    """
    Liste de tous les salaires
    """
    # Filtres
    mois_filter = request.GET.get('mois')
    annee_filter = request.GET.get('annee')
    statut_filter = request.GET.get('statut')
    employe_filter = request.GET.get('employe')

    salaires = Salaire.objects.all().select_related(
        'chauffeur', 'utilisateur', 'cree_par'
    ).prefetch_related('primes', 'deductions')

    # Appliquer les filtres
    if mois_filter:
        salaires = salaires.filter(mois=mois_filter)
    if annee_filter:
        salaires = salaires.filter(annee=annee_filter)
    if statut_filter:
        salaires = salaires.filter(statut=statut_filter)
    if employe_filter:
        salaires = salaires.filter(
            Q(chauffeur__nom__icontains=employe_filter) |
            Q(chauffeur__prenom__icontains=employe_filter) |
            Q(utilisateur__nom_utilisateur__icontains=employe_filter) |
            Q(utilisateur__email__icontains=employe_filter)
        )

    # Statistiques
    stats = {
        'total_salaires': salaires.count(),
        'total_paye': salaires.filter(statut='paye').aggregate(total=Sum('salaire_net'))['total'] or 0,
        'en_attente': salaires.filter(statut='brouillon').count(),
        'valides': salaires.filter(statut='valide').count(),
    }

    # Années disponibles pour le filtre
    annees_disponibles = Salaire.objects.values_list('annee', flat=True).distinct().order_by('-annee')

    context = {
        'salaires': salaires,
        'stats': stats,
        'annees_disponibles': annees_disponibles,
        'mois_choices': dict(Salaire._meta.get_field('mois').choices),
        'statut_choices': dict(Salaire._meta.get_field('statut').choices),
    }

    return render(request, 'transport/salaires/salaire_list.html', context)


@login_required
@role_required('ADMIN', 'COMPTABLE')
def salaire_create(request):
    """
    Créer un nouveau salaire
    """
    if request.method == 'POST':
        # Récupérer les données
        type_employe = request.POST.get('type_employe')
        chauffeur_id = request.POST.get('chauffeur')
        utilisateur_id = request.POST.get('utilisateur')
        mois = int(request.POST.get('mois'))
        annee = int(request.POST.get('annee'))
        salaire_base = Decimal(request.POST.get('salaire_base', 0))
        heures_supp = Decimal(request.POST.get('heures_supplementaires', 0))
        taux_heure_supp = Decimal(request.POST.get('taux_heure_supp', 0))
        mode_paiement = request.POST.get('mode_paiement', '')
        notes = request.POST.get('notes', '')

        # Validation
        errors = []

        if type_employe == 'chauffeur' and not chauffeur_id:
            errors.append("Veuillez sélectionner un chauffeur")
        elif type_employe == 'utilisateur' and not utilisateur_id:
            errors.append("Veuillez sélectionner un employé")

        # Vérifier si un salaire existe déjà pour cette période
        existing_query = Salaire.objects.filter(mois=mois, annee=annee)
        if type_employe == 'chauffeur' and chauffeur_id:
            existing_query = existing_query.filter(chauffeur_id=chauffeur_id)
        elif type_employe == 'utilisateur' and utilisateur_id:
            existing_query = existing_query.filter(utilisateur_id=utilisateur_id)

        if existing_query.exists():
            errors.append(f"Un salaire existe déjà pour cette personne pour {dict(Salaire._meta.get_field('mois').choices)[mois]} {annee}")

        if errors:
            for error in errors:
                messages.error(request, error)
            context = {
                'chauffeurs': Chauffeur.objects.filter(statut='ACTIF').order_by('nom'),
                'utilisateurs': Utilisateur.objects.filter(is_active=True).exclude(pk_utilisateur='').order_by('nom_utilisateur'),
                'mois_choices': Salaire._meta.get_field('mois').choices,
                'mode_paiement_choices': Salaire._meta.get_field('mode_paiement').choices,
                'form_data': request.POST,
            }
            return render(request, 'transport/salaires/salaire_form.html', context)

        try:
            # Créer le salaire
            salaire = Salaire(
                mois=mois,
                annee=annee,
                salaire_base=salaire_base,
                heures_supplementaires=heures_supp,
                taux_heure_supp=taux_heure_supp,
                mode_paiement=mode_paiement if mode_paiement else None,
                notes=notes,
                cree_par=request.user
            )

            if type_employe == 'chauffeur':
                salaire.chauffeur_id = chauffeur_id
            else:
                salaire.utilisateur_id = utilisateur_id

            salaire.save()

            messages.success(request, f"✅ Salaire créé pour {salaire.get_employe_nom()} - {salaire.get_periode()}")
            return redirect('salaire_detail', pk=salaire.pk_salaire)

        except Exception as e:
            messages.error(request, f"❌ Erreur: {str(e)}")

    context = {
        'chauffeurs': Chauffeur.objects.filter(statut='ACTIF').order_by('nom'),
        'utilisateurs': Utilisateur.objects.filter(is_active=True).exclude(pk_utilisateur='').order_by('nom_utilisateur'),
        'mois_choices': Salaire._meta.get_field('mois').choices,
        'mode_paiement_choices': Salaire._meta.get_field('mode_paiement').choices,
        'annee_actuelle': datetime.now().year,
        'mois_actuel': datetime.now().month,
        'form_data': {},
    }

    return render(request, 'transport/salaires/salaire_form.html', context)


@login_required
@role_required('ADMIN', 'COMPTABLE')
def salaire_detail(request, pk):
    """
    Détails d'un salaire avec gestion des primes et déductions
    """
    salaire = get_object_or_404(
        Salaire.objects.select_related('chauffeur', 'utilisateur', 'cree_par').prefetch_related('primes', 'deductions'),
        pk_salaire=pk
    )

    # Calcul des montants
    montant_heures_supp = salaire.heures_supplementaires * salaire.taux_heure_supp
    salaire_brut = salaire.salaire_base + montant_heures_supp + salaire.total_primes

    context = {
        'salaire': salaire,
        'montant_heures_supp': montant_heures_supp,
        'salaire_brut': salaire_brut,
    }

    return render(request, 'transport/salaires/salaire_detail.html', context)


@login_required
@role_required('ADMIN', 'COMPTABLE')
def salaire_update(request, pk):
    """
    Modifier un salaire existant
    """
    salaire = get_object_or_404(Salaire, pk_salaire=pk)

    if request.method == 'POST':
        try:
            salaire.salaire_base = Decimal(request.POST.get('salaire_base', 0))
            salaire.heures_supplementaires = Decimal(request.POST.get('heures_supplementaires', 0))
            salaire.taux_heure_supp = Decimal(request.POST.get('taux_heure_supp', 0))
            salaire.mode_paiement = request.POST.get('mode_paiement') or None
            salaire.notes = request.POST.get('notes', '')

            salaire.save()

            messages.success(request, f"✅ Salaire modifié avec succès")
            return redirect('salaire_detail', pk=salaire.pk_salaire)

        except Exception as e:
            messages.error(request, f"❌ Erreur: {str(e)}")

    context = {
        'salaire': salaire,
        'mode_paiement_choices': Salaire._meta.get_field('mode_paiement').choices,
        'is_update': True,
    }

    return render(request, 'transport/salaires/salaire_form.html', context)


@login_required
@role_required('ADMIN', 'COMPTABLE')
def salaire_delete(request, pk):
    """
    Supprimer un salaire
    """
    salaire = get_object_or_404(Salaire, pk_salaire=pk)

    if request.method == 'POST':
        try:
            employe_nom = salaire.get_employe_nom()
            periode = salaire.get_periode()
            salaire.delete()
            messages.success(request, f"✅ Salaire de {employe_nom} pour {periode} supprimé")
            return redirect('salaire_list')
        except Exception as e:
            messages.error(request, f"❌ Erreur: {str(e)}")

    context = {'salaire': salaire}
    return render(request, 'transport/salaires/salaire_confirm_delete.html', context)


@login_required
@role_required('ADMIN', 'COMPTABLE')
def salaire_valider(request, pk):
    """
    Valider un salaire (passe de brouillon à validé)
    """
    salaire = get_object_or_404(Salaire, pk_salaire=pk)

    if salaire.statut == 'brouillon':
        salaire.statut = 'valide'
        salaire.save()
        messages.success(request, f"✅ Salaire validé pour {salaire.get_employe_nom()}")
    else:
        messages.warning(request, "⚠️ Ce salaire est déjà validé")

    return redirect('salaire_detail', pk=pk)


@login_required
@role_required('ADMIN', 'COMPTABLE')
def salaire_payer(request, pk):
    """
    Marquer un salaire comme payé
    """
    salaire = get_object_or_404(Salaire, pk_salaire=pk)

    if request.method == 'POST':
        date_paiement = request.POST.get('date_paiement')
        mode_paiement = request.POST.get('mode_paiement')

        salaire.statut = 'paye'
        salaire.date_paiement = date_paiement
        if mode_paiement:
            salaire.mode_paiement = mode_paiement
        salaire.save()

        messages.success(request, f"✅ Paiement enregistré pour {salaire.get_employe_nom()}")
        return redirect('salaire_detail', pk=pk)

    context = {
        'salaire': salaire,
        'mode_paiement_choices': Salaire._meta.get_field('mode_paiement').choices,
    }
    return render(request, 'transport/salaires/salaire_payer.html', context)


@login_required
@role_required('ADMIN', 'COMPTABLE')
def prime_add(request, salaire_pk):
    """
    Ajouter une prime à un salaire
    """
    salaire = get_object_or_404(Salaire, pk_salaire=salaire_pk)

    if request.method == 'POST':
        type_prime = request.POST.get('type_prime')
        montant = Decimal(request.POST.get('montant', 0))
        description = request.POST.get('description', '')

        Prime.objects.create(
            salaire=salaire,
            type_prime=type_prime,
            montant=montant,
            description=description
        )

        messages.success(request, f"✅ Prime ajoutée: {type_prime} - {montant} FCFA")
        return redirect('salaire_detail', pk=salaire_pk)

    return redirect('salaire_detail', pk=salaire_pk)


@login_required
@role_required('ADMIN', 'COMPTABLE')
def prime_delete(request, pk):
    """
    Supprimer une prime
    """
    prime = get_object_or_404(Prime, pk_prime=pk)
    salaire_pk = prime.salaire.pk_salaire
    prime.delete()
    messages.success(request, "✅ Prime supprimée")
    return redirect('salaire_detail', pk=salaire_pk)


@login_required
@role_required('ADMIN', 'COMPTABLE')
def deduction_add(request, salaire_pk):
    """
    Ajouter une déduction à un salaire
    """
    salaire = get_object_or_404(Salaire, pk_salaire=salaire_pk)

    if request.method == 'POST':
        type_deduction = request.POST.get('type_deduction')
        montant = Decimal(request.POST.get('montant', 0))
        description = request.POST.get('description', '')

        Deduction.objects.create(
            salaire=salaire,
            type_deduction=type_deduction,
            montant=montant,
            description=description
        )

        messages.success(request, f"✅ Déduction ajoutée: {type_deduction} - {montant} FCFA")
        return redirect('salaire_detail', pk=salaire_pk)

    return redirect('salaire_detail', pk=salaire_pk)


@login_required
@role_required('ADMIN', 'COMPTABLE')
def deduction_delete(request, pk):
    """
    Supprimer une déduction
    """
    deduction = get_object_or_404(Deduction, pk_deduction=pk)
    salaire_pk = deduction.salaire.pk_salaire
    deduction.delete()
    messages.success(request, "✅ Déduction supprimée")
    return redirect('salaire_detail', pk=salaire_pk)

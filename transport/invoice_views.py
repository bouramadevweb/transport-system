"""
Vues pour la gestion des factures
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, FileResponse
from django.contrib import messages
from transport.models import PaiementMission
from transport.permissions import role_required, permission_required
from transport.invoice_generator import InvoiceGenerator, generate_invoice_for_payment
from transport.email_notifications import EmailNotifier
from django.core.mail import EmailMessage
from django.conf import settings


@login_required
@role_required('ADMIN', 'COMPTABLE')
def generate_invoice(request, paiement_id):
    """
    Génère une facture PDF pour un paiement
    """
    paiement = get_object_or_404(PaiementMission, pk_paiement=paiement_id)

    # Vérifier que le paiement est validé
    if not paiement.est_valide:
        messages.error(request, "❌ Impossible de générer une facture pour un paiement non validé.")
        return redirect('paiement_mission_list')

    try:
        # Générer la facture
        generator = InvoiceGenerator(paiement)
        pdf_file = generator.generate()
        filename = generator.get_filename()

        # Retourner le PDF en téléchargement
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        messages.success(request, f"✅ Facture {generator.generate_invoice_number()} générée avec succès!")

        return response

    except Exception as e:
        messages.error(request, f"❌ Erreur lors de la génération de la facture: {str(e)}")
        return redirect('paiement_mission_list')


@login_required
@role_required('ADMIN', 'COMPTABLE')
def preview_invoice(request, paiement_id):
    """
    Prévisualise une facture PDF dans le navigateur
    """
    paiement = get_object_or_404(PaiementMission, pk_paiement=paiement_id)

    try:
        # Générer la facture
        generator = InvoiceGenerator(paiement)
        pdf_file = generator.generate()

        # Retourner le PDF pour affichage dans le navigateur
        return FileResponse(pdf_file, content_type='application/pdf')

    except Exception as e:
        messages.error(request, f"❌ Erreur lors de la prévisualisation: {str(e)}")
        return redirect('paiement_mission_list')


@login_required
@role_required('ADMIN', 'COMPTABLE')
def send_invoice_email(request, paiement_id):
    """
    Envoie la facture par email au client et au chauffeur
    """
    paiement = get_object_or_404(PaiementMission, pk_paiement=paiement_id)

    # Vérifier que le paiement est validé
    if not paiement.est_valide:
        messages.error(request, "❌ Impossible d'envoyer une facture pour un paiement non validé.")
        return redirect('paiement_mission_list')

    try:
        # Générer la facture PDF
        generator = InvoiceGenerator(paiement)
        pdf_file = generator.generate()
        filename = generator.get_filename()
        invoice_number = generator.generate_invoice_number()

        # Préparer les destinataires
        recipients = []

        # Client
        if paiement.mission and paiement.mission.contrat and paiement.mission.contrat.client:
            client = paiement.mission.contrat.client
            if client.email:
                recipients.append(client.email)

        # Chauffeur
        if paiement.mission and paiement.mission.contrat and paiement.mission.contrat.chauffeur:
            chauffeur = paiement.mission.contrat.chauffeur
            if hasattr(chauffeur, 'email') and chauffeur.email:
                recipients.append(chauffeur.email)

        # Admin (copie)
        admin_email = 'admin@transport-system.com'
        if admin_email not in recipients:
            recipients.append(admin_email)

        if not recipients:
            messages.warning(request, "⚠️ Aucune adresse email disponible pour l'envoi.")
            return redirect('paiement_mission_list')

        # Créer l'email
        subject = f"📄 Facture {invoice_number} - TransportPro"
        message = f"""
        Bonjour,

        Veuillez trouver ci-joint votre facture {invoice_number}.

        Détails du paiement:
        - Montant total: {paiement.montant_total:,.0f} FCFA
        - Date de paiement: {paiement.date_paiement.strftime('%d/%m/%Y') if paiement.date_paiement else 'Non définie'}
        - Mode de paiement: {paiement.mode_paiement.upper() if paiement.mode_paiement else 'Non défini'}

        Merci de votre confiance.

        ---
        TransportPro - Système de Gestion de Transport
        Cet email a été généré automatiquement.
        """

        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipients,
        )

        # Attacher le PDF
        pdf_file.seek(0)
        email.attach(filename, pdf_file.read(), 'application/pdf')

        # Envoyer
        email.send()

        messages.success(request, f"✅ Facture {invoice_number} envoyée par email à {len(recipients)} destinataire(s)!")

    except Exception as e:
        messages.error(request, f"❌ Erreur lors de l'envoi de la facture: {str(e)}")

    return redirect('paiement_mission_list')


@login_required
@role_required('ADMIN', 'COMPTABLE')
def invoices_list(request):
    """
    Liste des factures (paiements validés)
    """
    # Paiements validés uniquement
    paiements = PaiementMission.objects.filter(
        est_valide=True
    ).select_related(
        'mission',
        'mission__contrat',
        'mission__contrat__client',
        'mission__contrat__chauffeur'
    ).order_by('-date_validation')

    context = {
        'paiements': paiements,
        'total_factures': paiements.count(),
    }

    return render(request, 'transport/invoices/list.html', context)


@login_required
@role_required('ADMIN', 'COMPTABLE')
def bulk_send_invoices(request):
    """
    Envoi en masse de factures
    """
    if request.method == 'POST':
        paiement_ids = request.POST.getlist('paiement_ids')

        if not paiement_ids:
            messages.error(request, "❌ Aucun paiement sélectionné.")
            return redirect('invoices_list')

        success_count = 0
        error_count = 0

        for paiement_id in paiement_ids:
            try:
                paiement = PaiementMission.objects.get(pk_paiement=paiement_id)

                # Générer et envoyer la facture
                generator = InvoiceGenerator(paiement)
                pdf_file = generator.generate()
                filename = generator.get_filename()

                # Préparer les destinataires
                recipients = []
                if paiement.mission and paiement.mission.contrat:
                    if paiement.mission.contrat.client and paiement.mission.contrat.client.email:
                        recipients.append(paiement.mission.contrat.client.email)
                    if paiement.mission.contrat.chauffeur:
                        chauffeur = paiement.mission.contrat.chauffeur
                        if hasattr(chauffeur, 'email') and chauffeur.email:
                            recipients.append(chauffeur.email)

                if recipients:
                    email = EmailMessage(
                        subject=f"📄 Facture {generator.generate_invoice_number()}",
                        body="Veuillez trouver ci-joint votre facture.",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=recipients,
                    )
                    pdf_file.seek(0)
                    email.attach(filename, pdf_file.read(), 'application/pdf')
                    email.send()

                    success_count += 1
                else:
                    error_count += 1
                    print(f"⚠️ Paiement {paiement_id}: Aucun destinataire trouvé (client ou chauffeur sans email)")

            except Exception as e:
                error_count += 1
                print(f"❌ Erreur envoi facture {paiement_id}: {str(e)}")
                import traceback
                traceback.print_exc()
                continue

        if success_count > 0:
            messages.success(request, f"✅ {success_count} facture(s) envoyée(s) avec succès!")
        if error_count > 0:
            messages.warning(request, f"⚠️ {error_count} facture(s) n'ont pas pu être envoyées (vérifiez les emails ou la console pour les détails).")

        if success_count == 0 and error_count == 0:
            messages.info(request, "ℹ️ Aucune facture n'a été traitée.")

        return redirect('invoices_list')

    return redirect('invoices_list')

"""
Générateur de factures PDF professionnelles
"""
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfgen import canvas
from django.core.files.base import ContentFile


class InvoiceGenerator:
    """
    Générateur de factures PDF
    """

    def __init__(self, paiement):
        """
        Initialise le générateur avec un paiement
        """
        self.paiement = paiement
        self.mission = paiement.mission
        self.contrat = self.mission.contrat if self.mission else None
        self.buffer = BytesIO()

    def generate_invoice_number(self):
        """
        Génère un numéro de facture unique
        Format: FAC-YYYY-NNNNNN
        """
        year = datetime.now().year
        # Utiliser pk_paiement pour un numéro unique
        numero = str(self.paiement.pk_paiement)[-6:].zfill(6)
        return f"FAC-{year}-{numero}"

    def generate(self):
        """
        Génère le PDF de la facture
        Retourne un ContentFile prêt à être sauvegardé
        """
        # Créer le document PDF
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        # Préparer les éléments
        elements = []
        styles = getSampleStyleSheet()

        # Style personnalisé pour le titre
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=30,
            alignment=TA_CENTER
        )

        # Style pour les informations
        info_style = ParagraphStyle(
            'Info',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=12
        )

        # === EN-TÊTE ===
        invoice_number = self.generate_invoice_number()
        title = Paragraph(f"<b>FACTURE</b><br/><font size=14>{invoice_number}</font>", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.5*cm))

        # === INFORMATIONS GÉNÉRALES ===
        date_facture = datetime.now().strftime('%d/%m/%Y')

        info_data = [
            [Paragraph('<b>Date de facture:</b>', info_style), date_facture],
            [Paragraph('<b>Date de paiement:</b>', info_style), self.paiement.date_paiement.strftime('%d/%m/%Y') if self.paiement.date_paiement else '-'],
            [Paragraph('<b>Mode de paiement:</b>', info_style), self.paiement.mode_paiement.upper() if self.paiement.mode_paiement else '-'],
        ]

        info_table = Table(info_data, colWidths=[6*cm, 10*cm])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 1*cm))

        # === CLIENT ===
        if self.contrat and self.contrat.client:
            client = self.contrat.client
            elements.append(Paragraph('<b>CLIENT</b>', styles['Heading2']))
            client_info = f"<b>{client.nom}</b><br/>"
            client_info += f"Type: {client.get_type_client_display()}<br/>"
            if client.telephone:
                client_info += f"Téléphone: {client.telephone}<br/>"
            if client.email:
                client_info += f"Email: {client.email}"
            elements.append(Paragraph(client_info, info_style))
            elements.append(Spacer(1, 0.5*cm))

        # === CHAUFFEUR ===
        if self.contrat and self.contrat.chauffeur:
            chauffeur = self.contrat.chauffeur
            elements.append(Paragraph('<b>CHAUFFEUR</b>', styles['Heading2']))
            chauffeur_info = f"<b>{chauffeur.nom} {chauffeur.prenom}</b><br/>"
            if chauffeur.telephone:
                chauffeur_info += f"Téléphone: {chauffeur.telephone}"
            elements.append(Paragraph(chauffeur_info, info_style))
            elements.append(Spacer(1, 0.5*cm))

        # === DÉTAILS DE LA MISSION ===
        if self.mission:
            elements.append(Paragraph('<b>DÉTAILS DE LA MISSION</b>', styles['Heading2']))
            elements.append(Spacer(1, 0.3*cm))

            # Tronquer l'ID mission pour l'affichage
            mission_id = str(self.mission.pk_mission)
            if len(mission_id) > 20:
                mission_id_display = mission_id[:17] + "..."
            else:
                mission_id_display = mission_id

            mission_data = [
                [
                    Paragraph('<b>Réf. Mission</b>', styles['Normal']),
                    Paragraph('<b>Origine</b>', styles['Normal']),
                    Paragraph('<b>Destination</b>', styles['Normal']),
                    Paragraph('<b>Date départ</b>', styles['Normal'])
                ],
                [
                    mission_id_display,
                    self.mission.origine,
                    self.mission.destination,
                    self.mission.date_depart.strftime('%d/%m/%Y') if self.mission.date_depart else '-'
                ]
            ]

            mission_table = Table(mission_data, colWidths=[4*cm, 4*cm, 4*cm, 4*cm])
            mission_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(mission_table)
            elements.append(Spacer(1, 1*cm))

        # === DÉTAILS FINANCIERS ===
        elements.append(Paragraph('<b>DÉTAILS FINANCIERS</b>', styles['Heading2']))
        elements.append(Spacer(1, 0.3*cm))

        # Calculer les montants
        montant_total = float(self.paiement.montant_total) if self.paiement.montant_total else 0
        commission = float(self.paiement.commission_transitaire) if self.paiement.commission_transitaire else 0
        montant_net = montant_total - commission

        financial_data = [
            [
                Paragraph('<b>Description</b>', styles['Normal']),
                Paragraph('<b>Montant (FCFA)</b>', styles['Normal'])
            ],
            ['Montant Total Transport', f'{montant_total:,.0f}'.replace(',', ' ')],
            ['Commission Transitaire', f'{commission:,.0f}'.replace(',', ' ')],
            [
                Paragraph('<b>MONTANT NET À PAYER</b>', styles['Normal']),
                Paragraph(f'<b>{montant_net:,.0f}'.replace(',', ' ') + '</b>', styles['Normal'])
            ],
        ]

        financial_table = Table(financial_data, colWidths=[12*cm, 4*cm])
        financial_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, 2), colors.lightgrey),
            ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#764ba2')),
            ('TEXTCOLOR', (0, 3), (-1, 3), colors.whitesmoke),
            ('FONTNAME', (0, 3), (-1, 3), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 3), (-1, 3), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(financial_table)
        elements.append(Spacer(1, 2*cm))

        # === PIED DE PAGE ===
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )

        # Tronquer l'ID paiement s'il est trop long
        paiement_id = str(self.paiement.pk_paiement)
        if len(paiement_id) > 50:
            paiement_id_display = paiement_id[:47] + "..."
        else:
            paiement_id_display = paiement_id

        footer_text = f"<b>TransportPro - Système de Gestion de Transport</b><br/>"
        footer_text += f"Facture générée automatiquement le {date_facture}<br/>"
        footer_text += f"Référence: {paiement_id_display}"
        elements.append(Paragraph(footer_text, footer_style))

        # === NOTES ===
        elements.append(Spacer(1, 1*cm))
        note_style = ParagraphStyle(
            'Note',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.grey,
            alignment=TA_LEFT
        )
        note_text = "<b>Notes:</b><br/>"
        note_text += "- Cette facture est définitive et ne peut être modifiée<br/>"
        note_text += "- Conserver cette facture comme preuve de paiement<br/>"
        note_text += "- Pour toute question, contactez le service comptabilité"
        elements.append(Paragraph(note_text, note_style))

        # Générer le PDF
        doc.build(elements)

        # Récupérer le contenu
        self.buffer.seek(0)
        return self.buffer

    def get_filename(self):
        """
        Retourne le nom de fichier pour la facture
        """
        invoice_number = self.generate_invoice_number()
        return f'facture_{invoice_number}.pdf'


def generate_invoice_for_payment(paiement):
    """
    Fonction helper pour générer une facture pour un paiement

    Usage:
        pdf_file = generate_invoice_for_payment(paiement)
        # Sauvegarder ou envoyer le PDF
    """
    generator = InvoiceGenerator(paiement)
    return generator.generate()

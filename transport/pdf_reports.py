"""
Génération de rapports PDF avancés
=====================================
"""

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime
from io import BytesIO
from .models import Mission, PaiementMission


@login_required
def generate_missions_report_pdf(request):
    """Génère un rapport PDF détaillé des missions avec statistiques"""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from reportlab.platypus import Image as RLImage
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
        from reportlab.pdfgen import canvas
    except ImportError:
        return HttpResponse("❌ Bibliothèque reportlab non installée. Exécutez: pip install reportlab", status=500)

    from .filters import MissionFilter

    # Récupérer les missions filtrées
    missions = Mission.objects.select_related(
        'contrat', 'contrat__chauffeur', 'contrat__client', 'contrat__camion', 'contrat__conteneur'
    ).order_by('-date_depart')

    # Appliquer les filtres
    missions = MissionFilter.apply(missions, request)

    # Créer le buffer
    buffer = BytesIO()

    # Créer le document en paysage pour plus d'espace
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading3'],
        fontSize=11,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=8,
        fontName='Helvetica-Bold'
    )

    # Contenu du document
    story = []

    # En-tête du rapport
    story.append(Paragraph("📊 RAPPORT DES MISSIONS", title_style))
    story.append(Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 0.5*cm))

    # Statistiques globales
    total_missions = missions.count()
    missions_en_cours = missions.filter(statut='en cours').count()
    missions_terminees = missions.filter(statut='terminée').count()
    missions_annulees = missions.filter(statut='annulée').count()

    stats_data = [
        ['Statistiques Globales', '', '', ''],
        ['Total Missions', 'En Cours', 'Terminées', 'Annulées'],
        [str(total_missions), str(missions_en_cours), str(missions_terminees), str(missions_annulees)]
    ]

    stats_table = Table(stats_data, colWidths=[5*cm, 4*cm, 4*cm, 4*cm])
    stats_table.setStyle(TableStyle([
        # En-tête principal
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('SPAN', (0, 0), (-1, 0)),

        # Sous-en-têtes
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#dbeafe')),
        ('TEXTCOLOR', (0, 1), (-1, 1), colors.HexColor('#1e40af')),
        ('ALIGN', (0, 1), (-1, 1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, 1), 10),

        # Données
        ('BACKGROUND', (0, 2), (-1, 2), colors.white),
        ('ALIGN', (0, 2), (-1, 2), 'CENTER'),
        ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 2), (-1, 2), 14),
        ('TEXTCOLOR', (0, 2), (0, 2), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (1, 2), (1, 2), colors.HexColor('#f59e0b')),
        ('TEXTCOLOR', (2, 2), (2, 2), colors.HexColor('#10b981')),
        ('TEXTCOLOR', (3, 2), (3, 2), colors.HexColor('#ef4444')),

        # Bordures
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#3b82f6')),
        ('LINEBELOW', (0, 1), (-1, 1), 1, colors.HexColor('#3b82f6')),
        ('GRID', (0, 1), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),

        # Padding
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))

    story.append(stats_table)
    story.append(Spacer(1, 0.8*cm))

    # Tableau des missions
    if missions:
        story.append(Paragraph("Détail des Missions", subtitle_style))
        story.append(Spacer(1, 0.3*cm))

        # En-têtes du tableau
        data = [
            ['ID', 'Statut', 'Origine', 'Destination', 'Date Départ', 'Date Retour', 'Chauffeur', 'Client']
        ]

        # Données
        for mission in missions[:50]:  # Limiter à 50 pour ne pas surcharger
            statut_color = {
                'en cours': '🟡',
                'terminée': '🟢',
                'annulée': '🔴'
            }.get(mission.statut, '⚪')

            data.append([
                mission.pk_mission[:12] + '...',
                f"{statut_color} {mission.statut}",
                mission.origine[:15],
                mission.destination[:15],
                mission.date_depart.strftime('%d/%m/%Y') if mission.date_depart else '-',
                mission.date_retour.strftime('%d/%m/%Y') if mission.date_retour else '-',
                f"{mission.contrat.chauffeur.nom} {mission.contrat.chauffeur.prenom}"[:20] if mission.contrat and mission.contrat.chauffeur else '-',
                mission.contrat.client.nom[:15] if mission.contrat and mission.contrat.client else '-'
            ])

        # Créer le tableau
        table = Table(data, colWidths=[3.2*cm, 2.5*cm, 3*cm, 3*cm, 2.5*cm, 2.5*cm, 3.5*cm, 3*cm])
        table.setStyle(TableStyle([
            # En-tête
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),

            # Données
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

            # Bordures
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#3b82f6')),
            ('GRID', (0, 1), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),

            # Padding
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),

            # Lignes alternées
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ]))

        story.append(table)

        if missions.count() > 50:
            story.append(Spacer(1, 0.3*cm))
            story.append(Paragraph(
                f"<i>Note: Affichage limité aux 50 premières missions sur {missions.count()} au total.</i>",
                styles['Normal']
            ))
    else:
        story.append(Paragraph("Aucune mission trouvée avec les filtres appliqués.", styles['Normal']))

    # Pied de page avec informations
    story.append(Spacer(1, 1*cm))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#64748b'),
        alignment=TA_CENTER
    )
    story.append(Paragraph(
        f"Document généré automatiquement par le système de gestion TransportPro - {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        footer_style
    ))

    # Construire le PDF
    doc.build(story)

    # Retourner la réponse
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=rapport_missions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'

    return response


@login_required
def generate_paiements_report_pdf(request):
    """Génère un rapport PDF détaillé des paiements avec statistiques"""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
    except ImportError:
        return HttpResponse("❌ Bibliothèque reportlab non installée. Exécutez: pip install reportlab", status=500)

    from .filters import PaiementMissionFilter

    # Récupérer les paiements filtrés
    paiements = PaiementMission.objects.select_related(
        'mission', 'mission__contrat__chauffeur', 'caution'
    ).order_by('-date_paiement')

    # Appliquer les filtres
    paiements = PaiementMissionFilter.apply(paiements, request)

    # Créer le buffer
    buffer = BytesIO()

    # Créer le document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#10b981'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )

    # Contenu du document
    story = []

    # En-tête du rapport
    story.append(Paragraph("💰 RAPPORT DES PAIEMENTS", title_style))
    story.append(Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 0.5*cm))

    # Statistiques globales
    total_paiements = paiements.count()
    paiements_valides = paiements.filter(est_valide=True).count()
    paiements_attente = paiements.filter(est_valide=False).count()

    # Calculs financiers
    montant_total = sum(float(p.montant_total) for p in paiements)
    commission_total = sum(float(p.commission_transitaire) for p in paiements)
    montant_valide = sum(float(p.montant_total) for p in paiements.filter(est_valide=True))

    stats_data = [
        ['Statistiques Financières', '', '', ''],
        ['Total Paiements', 'Validés', 'En Attente', 'Montant Total'],
        [str(total_paiements), str(paiements_valides), str(paiements_attente), f"{montant_total:,.0f} FCFA"],
        ['', 'Montant Validé', 'Commission Totale', ''],
        ['', f"{montant_valide:,.0f} FCFA", f"{commission_total:,.0f} FCFA", '']
    ]

    stats_table = Table(stats_data, colWidths=[5*cm, 5*cm, 5*cm, 5*cm])
    stats_table.setStyle(TableStyle([
        # En-tête principal
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('SPAN', (0, 0), (-1, 0)),

        # Sous-en-têtes ligne 1
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#d1fae5')),
        ('TEXTCOLOR', (0, 1), (-1, 1), colors.HexColor('#065f46')),
        ('ALIGN', (0, 1), (-1, 1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, 1), 9),

        # Données ligne 2
        ('BACKGROUND', (0, 2), (-1, 2), colors.white),
        ('ALIGN', (0, 2), (-1, 2), 'CENTER'),
        ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 2), (-1, 2), 11),
        ('TEXTCOLOR', (0, 2), (0, 2), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (1, 2), (1, 2), colors.HexColor('#10b981')),
        ('TEXTCOLOR', (2, 2), (2, 2), colors.HexColor('#f59e0b')),
        ('TEXTCOLOR', (3, 2), (3, 2), colors.HexColor('#059669')),

        # Sous-en-têtes ligne 3
        ('BACKGROUND', (1, 3), (2, 3), colors.HexColor('#d1fae5')),
        ('TEXTCOLOR', (1, 3), (2, 3), colors.HexColor('#065f46')),
        ('ALIGN', (1, 3), (2, 3), 'CENTER'),
        ('FONTNAME', (1, 3), (2, 3), 'Helvetica-Bold'),
        ('FONTSIZE', (1, 3), (2, 3), 9),

        # Données ligne 4
        ('BACKGROUND', (1, 4), (2, 4), colors.white),
        ('ALIGN', (1, 4), (2, 4), 'CENTER'),
        ('FONTNAME', (1, 4), (2, 4), 'Helvetica-Bold'),
        ('FONTSIZE', (1, 4), (2, 4), 11),
        ('TEXTCOLOR', (1, 4), (1, 4), colors.HexColor('#059669')),
        ('TEXTCOLOR', (2, 4), (2, 4), colors.HexColor('#dc2626')),

        # Bordures
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#10b981')),
        ('LINEBELOW', (0, 1), (-1, 1), 1, colors.HexColor('#10b981')),
        ('LINEBELOW', (0, 3), (-1, 3), 1, colors.HexColor('#10b981')),
        ('GRID', (0, 1), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),

        # Padding
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))

    story.append(stats_table)
    story.append(Spacer(1, 0.8*cm))

    # Tableau des paiements
    if paiements:
        story.append(Paragraph("Détail des Paiements", subtitle_style))
        story.append(Spacer(1, 0.3*cm))

        # En-têtes du tableau
        data = [
            ['ID Paiement', 'Mission', 'Montant', 'Commission', 'Caution', 'Statut', 'Date', 'Chauffeur']
        ]

        # Données
        for paiement in paiements[:50]:  # Limiter à 50
            statut_icon = '✅' if paiement.est_valide else '⏳'

            data.append([
                paiement.pk_paiement[:12] + '...',
                paiement.mission.pk_mission[:12] + '...' if paiement.mission else '-',
                f"{float(paiement.montant_total):,.0f} F",
                f"{float(paiement.commission_transitaire):,.0f} F",
                'Oui' if paiement.caution_est_retiree else 'Non',
                f"{statut_icon} {'Validé' if paiement.est_valide else 'Attente'}",
                paiement.date_paiement.strftime('%d/%m/%Y') if paiement.date_paiement else '-',
                f"{paiement.mission.contrat.chauffeur.nom} {paiement.mission.contrat.chauffeur.prenom}"[:18] if paiement.mission and paiement.mission.contrat and paiement.mission.contrat.chauffeur else '-'
            ])

        # Créer le tableau
        table = Table(data, colWidths=[3*cm, 3*cm, 2.8*cm, 2.8*cm, 2*cm, 2.5*cm, 2.5*cm, 3.5*cm])
        table.setStyle(TableStyle([
            # En-tête
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),

            # Données
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (1, -1), 'LEFT'),
            ('ALIGN', (2, 1), (3, -1), 'RIGHT'),
            ('ALIGN', (4, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

            # Bordures
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#10b981')),
            ('GRID', (0, 1), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),

            # Padding
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),

            # Lignes alternées
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ]))

        story.append(table)

        if paiements.count() > 50:
            story.append(Spacer(1, 0.3*cm))
            story.append(Paragraph(
                f"<i>Note: Affichage limité aux 50 premiers paiements sur {paiements.count()} au total.</i>",
                styles['Normal']
            ))
    else:
        story.append(Paragraph("Aucun paiement trouvé avec les filtres appliqués.", styles['Normal']))

    # Pied de page
    story.append(Spacer(1, 1*cm))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#64748b'),
        alignment=TA_CENTER
    )
    story.append(Paragraph(
        f"Document généré automatiquement par le système de gestion TransportPro - {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        footer_style
    ))

    # Construire le PDF
    doc.build(story)

    # Retourner la réponse
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=rapport_paiements_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'

    return response

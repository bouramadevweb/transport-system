from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import os

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect,get_object_or_404
from django.db import IntegrityError
from django.contrib import messages
from transport.models import Chauffeur, Entreprise,Camion,Affectation,Transitaire,Client,CompagnieConteneur,Conteneur,ContratTransport,PrestationDeTransports,Cautions,FraisTrajet,Mission,MissionConteneur,PaiementMission,Mecanicien,Fournisseur,Reparation,ReparationMecanicien,PieceReparee
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from datetime import datetime
from django.contrib.auth.views import LogoutView
from django.contrib.auth import logout
from django.shortcuts import redirect

from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from io import BytesIO
from django.conf import settings
import os

# def generate_pdf_contrat(contrat, output_path):
#     styles = getSampleStyleSheet()
#     story = []

#     story.append(Paragraph(f"<b>FEUILLE DE ROUTE</b>", styles["Title"]))
#     story.append(Spacer(1, 12))

#     # Informations principales
#     story.append(Paragraph(f"<b>BL :</b> {contrat.numero_bl}", styles["Normal"]))
#     story.append(Paragraph(f"<b>Destinataire :</b> {contrat.destinataire}", styles["Normal"]))
#     story.append(Paragraph(f"<b>Chauffeur :</b> {contrat.chauffeur.nom} {contrat.chauffeur.prenom}", styles["Normal"]))
#     story.append(Paragraph(f"<b>Camion :</b> {contrat.camion.immatriculation}", styles["Normal"]))
#     story.append(Spacer(1, 12))

#     # Tableau de montants
#     table = Table([
#         ["Désignation", "Montant"],
#         ["Montant total", f"{contrat.montant_total} FCFA"],
#         ["Avance transport", f"{contrat.avance_transport} FCFA"],
#         ["Reliquat", f"{contrat.reliquat_transport} FCFA"],
#         ["Caution", f"{contrat.caution} FCFA"],
#     ])

#     table.setStyle(TableStyle([
#         ("GRID", (0,0), (-1,-1), 1, colors.black),
#         ("BACKGROUND", (0,0), (-1,0), colors.grey),
#         ("ALIGN", (0,0), (-1,-1), "CENTER"),
#     ]))

#     story.append(table)
#     story.append(Spacer(1, 12))

#     doc = SimpleDocTemplate(output_path, pagesize=A4)
#     doc.build(story)



def generate_pdf_contrat(request, pk):
    contrat = get_object_or_404(ContratTransport, pk_contrat=pk)

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleCenter", alignment=1, fontSize=16, spaceAfter=12))
    styles.add(ParagraphStyle(name="NormalBold", fontSize=12))
    styles.add(ParagraphStyle(name="NormalJustify", alignment=4, leading=14))

    story = []

    # === TITRE ===
    story.append(Paragraph("<b>FEUILLE DE ROUTE</b>", styles["TitleCenter"]))
    story.append(Paragraph(f"{contrat.entreprise.nom}", styles["TitleCenter"]))
    story.append(Spacer(1, 10))

    # === DETAIL DESTINATAIRE ===
    story.append(Paragraph(f"<b>DESTINATAIRE :</b> {contrat.destinataire}", styles["Normal"]))
    story.append(Paragraph(f"<b>N° BL :</b> {contrat.numero_bl}", styles["Normal"]))
    story.append(Paragraph(f"<b>N° CONTENEUR(S) :</b> {contrat.conteneur.numero_conteneur}", styles["Normal"]))
    story.append(Paragraph(
        f"<b>NOM DU CHAUFFEUR :</b> {contrat.chauffeur.nom} {contrat.chauffeur.prenom} — Tel {contrat.chauffeur.telephone}",
        styles["Normal"]
    ))
    story.append(Paragraph(f"<b>NUMÉRO CAMION :</b> {contrat.camion.immatriculation}", styles["Normal"]))
    story.append(Spacer(1, 12))

    # === Tableau des montants ===
    data = [
        ["DÉSIGNATION", "MONTANT"],
        ["Montant total", f"{contrat.montant_total} FCFA"],
        ["Avance transport", f"{contrat.avance_transport} FCFA"],
        ["Reliquat transport", f"{contrat.reliquat_transport} FCFA"],
        ["Caution", f"{contrat.caution} FCFA"],
    ]

    table = Table(data, colWidths=[250, 150])
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.8, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    story.append(table)
    story.append(Spacer(1, 14))

    # === INFORMATIONS ===
    story.append(Paragraph(f"<b>Nature de la marchandise :</b> Produits divers", styles["Normal"]))
    story.append(Paragraph(f"<b>Transitaire :</b> {contrat.transitaire.nom} — {contrat.transitaire.telephone}", styles["Normal"]))
    story.append(Spacer(1, 12))

    # === CLAUSES ===
    text = """
    <b>NB : Clause de responsabilité et pénalité</b><br/><br/>
    • Le transporteur est responsable uniquement en cas de perte, vol ou avarie causée par négligence.<br/>
    • La responsabilité est proportionnelle à la part non couverte par l’assurance.<br/>
    • Pas de responsabilité en cas de force majeure, douane, port, ou tiers intervenants.<br/><br/>
    • Le transporteur dispose de <b>23 jours</b> pour ramener les conteneurs vides à Dakar.<br/>
    • Retard dû au destinataire → <b>25 000 FCFA/jour</b> à facturer.<br/>
    • Retard dû au transporteur → <b>25 000 FCFA/jour</b> de pénalité.<br/><br/>
    • Une fois à Bamako, le destinataire dispose de <b>3 jours</b> pour décharger. Après : <b>25 000 FCFA/jour</b>.
    """
    story.append(Paragraph(text, styles["NormalJustify"]))
    story.append(Spacer(1, 20))

    # === Dates et signatures ===
    story.append(Paragraph(f"<b>Date de chargement :</b> {contrat.date_debut}", styles["Normal"]))
    story.append(Paragraph(f"<b>Date de sortie :</b> {contrat.date_limite_retour}", styles["Normal"]))
    story.append(Spacer(1, 12))

    sign_table = Table(
        [["Signature transporteur", "Signature agent transit"],
         ["(signature)", "(signature)"]],
        colWidths=[250, 250]
    )
    sign_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("LINEBELOW", (0, 1), (-1, 1), 0.8, colors.black),
    ]))

    story.append(sign_table)

    # Génération finale
    doc.build(story)

    buffer.seek(0)
    return HttpResponse(
        buffer,
        content_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename=\"Feuille_de_Route_{pk}.pdf\"'}
    )

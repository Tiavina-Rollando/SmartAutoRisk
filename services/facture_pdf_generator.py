import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generer_pdf_facture(facture_id, date_facture, plage_deb, plage_fin, proprio_nom, proprio_prenom, immatriculation, marque, modele, montant, statut, commentaire=""):
    """
    Génère le fichier PDF d'une facture sous le dossier 'documents/factures/'.
    """
    os.makedirs("documents/factures", exist_ok=True)
    pdf_path = f"documents/factures/facture_{facture_id}.pdf"
    
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'FactureTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#2C3E50'),
        alignment=0,
        spaceAfter=10
    )

    body_style = ParagraphStyle(
        'FactureBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#333333')
    )

    # En-tête : Titre et Référence
    story.append(Paragraph(f"<b>FACTURE N° FAC-{facture_id:05d}</b>", title_style))
    story.append(Paragraph(f"Date d'émission : <b>{date_facture}</b>", body_style))
    story.append(Spacer(1, 15))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#2C3E50'), spaceAfter=15))

    # Détails du Client & Véhicule
    statut_texte = "PAYÉE" if statut == 1 else "EN ATTENTE DE RÈGLEMENT"
    statut_couleur = colors.HexColor('#27AE60') if statut == 1 else colors.HexColor('#E74C3C')

    info_text = f"""
    <b>Client :</b> {proprio_nom.upper()} {proprio_prenom.title()}<br/>
    <b>Véhicule :</b> {marque} {modele} ({immatriculation})<br/>
    <b>Période couverte :</b> Du <b>{plage_deb}</b> au <b>{plage_fin}</b><br/>
    <b>Statut du paiement :</b> <font color="{statut_couleur}"><b>{statut_texte}</b></font>
    """
    story.append(Paragraph(info_text, body_style))
    story.append(Spacer(1, 20))

    # Tableau récapitulatif des montants
    data = [
        ["Désignation", "Période", "Montant (Ar)"],
        [f"Cotisation Assurance - {marque} {modele}", f"{plage_deb} à {plage_fin}", f"{montant:,.2f}"],
        ["TOTAL À PAYER", "", f"{montant:,.2f} Ar"]
    ]

    table = Table(data, colWidths=[240, 140, 120])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BDC3C7')),
        ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#ECF0F1')),
    ]))

    story.append(table)

    if commentaire:
        story.append(Spacer(1, 15))
        story.append(Paragraph(f"<b>Note :</b> {commentaire}", body_style))

    story.append(Spacer(1, 30))
    story.append(Paragraph("<i>Merci de votre confiance. Pour toute réclamation, veuillez contacter le service client SmartAutoRisk.</i>", body_style))

    doc.build(story)
    return pdf_path
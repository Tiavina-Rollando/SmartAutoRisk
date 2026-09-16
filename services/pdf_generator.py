import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generer_pdf_contrat(vehicule_id, date_contrat, proprio_nom, proprio_prenom, type_v, nom_vehicule, offre, modalite_paiement):
    """
    Génère un contrat d'assurance structuré sous forme de document texte officiel.
    """
    os.makedirs("documents", exist_ok=True)
    pdf_path = f"documents/contrat_{vehicule_id}.pdf"
    
    doc = SimpleDocTemplate(
        pdf_path, 
        pagesize=letter, 
        rightMargin=50, 
        leftMargin=50, 
        topMargin=50, 
        bottomMargin=50
    )
    story = []
    
    # Styles de texte
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'ContractTitle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1A252C'),
        alignment=1,
        spaceAfter=5
    )
    
    subtitle_style = ParagraphStyle(
        'ContractSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=12,
        textColor=colors.HexColor('#555555'),
        alignment=1,
        spaceAfter=15
    )

    section_style = ParagraphStyle(
        'ContractSection',
        parent=styles['Heading2'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#2C3E50'),
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'ContractBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=15,
        textColor=colors.HexColor('#2B2B2B'),
        alignment=4,  # Justifié
        spaceAfter=8
    )

    # 1. En-tête du document
    story.append(Paragraph("<b>CONTRAT D'ASSURANCE AUTOMOBILE</b>", title_style))
    story.append(Paragraph(f"Référence du Contrat : <b>CTR-{vehicule_id:05d}</b>", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#2C3E50'), spaceAfter=15))
    
    # 2. Préambule et Désignation des Parties
    p_parties = (
        f"<b>Entre les soussignés :</b><br/>"
        f"La compagnie d'assurance <b>SmartAutoRisk</b>, d'une part,<br/>"
        f"Et M./Mme <b>{proprio_nom.upper()} {proprio_prenom.title()}</b>, désigné(e) ci-après "
        f"comme « <b>le Souscripteur</b> », d'autre part.<br/><br/>"
        f"Il a été convenu et arrêté ce qui suit en date du <b>{date_contrat}</b> :"
    )
    story.append(Paragraph(p_parties, body_style))
    
    # 3. Article 1 : Objet du Contrat et Véhicule Assuré
    story.append(Paragraph("ARTICLE 1 : OBJET DU CONTRAT ET VÉHICULE ASSURÉ", section_style))
    p_article1 = (
        f"Le présent contrat a pour objet de couvrir les risques liés à la circulation et à la détention "
        f"du véhicule désigné ci-après, souscrit sous l'identifiant système <b>N° {vehicule_id}</b>.<br/>"
        f"• <b>Type de véhicule :</b> {type_v}<br/>"
        f"• <b>Marque et Modèle :</b> {nom_vehicule}"
    )
    story.append(Paragraph(p_article1, body_style))
    
    # 4. Article 2 : Formule de Garantie et Modalités de Paiement
    story.append(Paragraph("ARTICLE 2 : FORMULE ET MODALITÉS FINANCIÈRES", section_style))
    p_article2 = (
        f"Le Souscripteur opte pour la formule de couverture <b>« {offre} »</b>.<br/>"
        f"Le règlement des cotisations s'effectuera selon une périodicité <b>{modalite_paiement}</b>.<br/>"
        f"Le Souscripteur s'engage à honorer les échéances convenues afin de maintenir la validité des garanties."
    )
    story.append(Paragraph(p_article2, body_style))
    
    # 5. Article 3 : Prise d'Effet et Engagements
    story.append(Paragraph("ARTICLE 3 : PRISE D'EFFET ET ENGAGEMENTS", section_style))
    p_article3 = (
        f"Les garanties prennent effet à compter du <b>{date_contrat}</b>. "
        f"Le Souscripteur atteste de l'exactitude des informations fournies lors de la souscription. "
        f"Toute fausse déclaration intentionnelle pourra entraîner la nullité du présent contrat "
        f"conformément à la réglementation en vigueur."
    )
    story.append(Paragraph(p_article3, body_style))
    
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#CCCCCC'), spaceAfter=20))
    
    # 6. Bloc de Signatures
    signatures_text = (
        f"Fait le <b>{date_contrat}</b>, en deux exemplaires originaux.<br/><br/><br/>"
        f"<b>Le Souscripteur</b> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
        f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
        f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
        f"<b>Pour la Compagnie SmartAutoRisk</b><br/>"
        f"<i>(Signature précédée de « Lu et approuvé »)</i>"
    )
    story.append(Paragraph(signatures_text, body_style))
    
    # Génération effective du PDF
    doc.build(story)
    
    return pdf_path


def generer_pdf_facture(facture_id, date_facture, plage_deb, plage_fin, proprio_nom, proprio_prenom, immatriculation, nom_vehicule, montant):
    """
    Génère un reçu/facture de paiement officiel au format PDF.
    """
    os.makedirs("factures", exist_ok=True)
    pdf_path = f"factures/facture_{facture_id}.pdf"

    doc = SimpleDocTemplate(
        pdf_path, 
        pagesize=letter, 
        rightMargin=50, 
        leftMargin=50, 
        topMargin=50, 
        bottomMargin=50
    )
    story = []

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1A252C'),
        alignment=1,
        spaceAfter=5
    )

    subtitle_style = ParagraphStyle(
        'InvoiceSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=12,
        textColor=colors.HexColor('#555555'),
        alignment=1,
        spaceAfter=15
    )

    section_style = ParagraphStyle(
        'InvoiceSection',
        parent=styles['Heading2'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#2C3E50'),
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'InvoiceBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=15,
        textColor=colors.HexColor('#2B2B2B'),
        spaceAfter=8
    )

    # Formattage du montant
    montant_str = f"{montant:,.0f} Ar".replace(",", " ") if isinstance(montant, (int, float)) else str(montant)

    # En-tête
    story.append(Paragraph("<b>FACTURE & REÇU DE PAIEMENT</b>", title_style))
    story.append(Paragraph(f"Référence Facture : <b>FAC-{facture_id:05d}</b> | Date : <b>{date_facture}</b>", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#2C3E50'), spaceAfter=15))

    # Informations Souscripteur
    story.append(Paragraph("INFORMATIONS DU SOUSCRIPTEUR ET VÉHICULE", section_style))
    p_info = (
        f"• <b>Client / Souscripteur :</b> {proprio_nom.upper()} {proprio_prenom.title()}<br/>"
        f"• <b>Véhicule :</b> {nom_vehicule}<br/>"
        f"• <b>Immatriculation :</b> {immatriculation}"
    )
    story.append(Paragraph(p_info, body_style))

    # Détails du règlement
    story.append(Paragraph("DÉTAILS DE LA COUVERTURE ET RÈGLEMENT", section_style))
    p_reglement = (
        f"• <b>Période couverte :</b> Du <b>{plage_deb}</b> au <b>{plage_fin}</b><br/>"
        f"• <b>Statut du règlement :</b> <font color='#27AE60'><b>ACQUITTÉ / PAYÉ</b></font><br/>"
        f"• <b>Montant Total Réglé :</b> <font size=12 color='#1A252C'><b>{montant_str}</b></font>"
    )
    story.append(Paragraph(p_reglement, body_style))

    story.append(Spacer(1, 30))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#CCCCCC'), spaceAfter=20))

    # Tampon et validation
    tampon_text = (
        f"Document généré automatiquement par <b>SmartAutoRisk</b> le {date_facture}.<br/>"
        f"<i>Ce document fait office de quittance de paiement pour la période indiquée.</i>"
    )
    story.append(Paragraph(tampon_text, subtitle_style))

    doc.build(story)

    return pdf_path
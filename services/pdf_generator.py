from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generer_pdf_contrat(output_path, details, date_signature, tarif, type_paiement):
    """
    Génère un contrat d'assurance automobile au format PDF.
    """
    # Configuration de la page
    doc = SimpleDocTemplate(
        output_path, 
        pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )
    story = []
    
    # Styles typographiques
    styles = getSampleStyleSheet()
    
    style_titre = ParagraphStyle(
        'TitreContrat',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#2e6de6'), # Ton bleu principal d'interface
        alignment=1,
        spaceAfter=15
    )
    
    style_sous_titre = ParagraphStyle(
        'SousTitre',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.gray,
        alignment=1,
        spaceAfter=25
    )
    
    style_section = ParagraphStyle(
        'SectionContrat',
        parent=styles['Heading2'],
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#2e6de6'),
        spaceBefore=10,
        spaceAfter=5
    )

    style_texte = ParagraphStyle(
        'TexteContrat',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#2D3748')
    )

    # 1. En-tête
    story.append(Paragraph("CONTRAT D'ASSURANCE AUTOMOBILE", style_titre))
    story.append(Paragraph(f"SmartAutoRisk S.A. - Contrat N° SAR-{details['immatriculation']}-{date_signature.replace('-', '')}", style_sous_titre))
    story.append(Spacer(1, 10))

    # 2. Section Propriétaire
    story.append(Paragraph("1. LE SOUSCRIPTEUR", style_section))
    info_proprietaire = (
        f"<b>Nom & Prénom :</b> {details['nom_p']} {details['prenom_p']}<br/>"
        f"<b>Adresse :</b> {details['adresse_p']}<br/>"
        f"<b>Date de naissance :</b> {details['date_naissance_p']}<br/>"
        f"<b>Date d'obtention du permis :</b> {details['date_permis_p']}"
    )
    story.append(Paragraph(info_proprietaire, style_texte))
    story.append(Spacer(1, 10))

    # 3. Section Véhicule
    story.append(Paragraph("2. LE VÉHICULE ASSURÉ", style_section))
    info_vehicule = (
        f"<b>Marque & Modèle :</b> {details['marque']} {details['modele']}<br/>"
        f"<b>Type :</b> {details['type']}<br/>"
        f"<b>Immatriculation :</b> {details['immatriculation']}<br/>"
        f"<b>Puissance :</b> {details['puissance']} CV<br/>"
        f"<b>Cylindrée :</b> {details['cylindre']} cc<br/>"
        f"<b>Usage :</b> {details['usage']}<br/>"
        f"<b>Valeur du véhicule :</b> {details['valeur']} MGA"
    )
    story.append(Paragraph(info_vehicule, style_texte))
    story.append(Spacer(1, 10))

    # 4. Section Conditions Financières
    story.append(Paragraph("3. CONDITIONS FINANCIÈRES", style_section))
    info_financieres = (
        f"<b>Tarif appliqué :</b> {tarif} MGA<br/>"
        f"<b>Fréquence de paiement :</b> {type_paiement}<br/>"
        f"<b>Date d'effet du contrat :</b> {date_signature}"
    )
    story.append(Paragraph(info_financieres, style_texte))
    story.append(Spacer(1, 20))

    # 5. Signatures
    story.append(Paragraph("4. SIGNATURES", style_section))
    data_signatures = [
        [
            Paragraph("<b>Pour l'assureur (SmartAutoRisk) :</b>", style_texte),
            Paragraph("<b>Le Souscripteur (Précédé de la mention 'Lu et approuvé') :</b>", style_texte)
        ],
        [
            Paragraph("<br/><br/><i>Signature certifiée conforme</i>", style_texte),
            Paragraph("<br/><br/>Signature :", style_texte)
        ]
    ]
    
    table_signatures = Table(data_signatures, colWidths=[240, 240])
    table_signatures.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    
    story.append(table_signatures)

    # Génération du PDF final
    doc.build(story)
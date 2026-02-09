from sqlalchemy import Column, BigInteger, Date, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from .base import Base

class HistoriqueNiveauRisk(Base):
    __tablename__ = "historique_niveau_risks"

    id = Column(BigInteger, primary_key=True)
    vehicule_id = Column(BigInteger, ForeignKey("vehicules.id"))
    saison_id = Column(BigInteger, ForeignKey("saisons.id"))
    niveau_risk = Column(
        Enum("faible", "moyen", "élevé", name="niveau_risk_enum"),
        default="moyen"
    )
    source = Column(
        Enum("RNA", "règle", "PS", name="source_risk_enum"),
        default="règle"
    )
    date_evaluation = Column(Date, nullable=False)
    commentaire = Column(Text)

    vehicule = relationship("Vehicule", back_populates="risques")
    saison = relationship("Saison", back_populates="risques")
    frais = relationship("HistoriqueFrais", back_populates="historique_risk")

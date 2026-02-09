from sqlalchemy import Column, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class HistoriqueFrais(Base):
    __tablename__ = "historique_frais"

    id = Column(BigInteger, primary_key=True)
    frais = Column(BigInteger, nullable=False)
    historique_niveau_risk_id = Column(
        BigInteger,
        ForeignKey("historique_niveau_risks.id")
    )

    historique_risk = relationship("HistoriqueNiveauRisk", back_populates="frais")

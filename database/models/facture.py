from sqlalchemy import Column, BigInteger, Date, Boolean, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Facture(Base):
    __tablename__ = "factures"

    id = Column(BigInteger, primary_key=True)
    date = Column(Date, nullable=False)
    plage_deb = Column(Date, nullable=False)
    plage_fin = Column(Date, nullable=False)
    contrat_id = Column(BigInteger, ForeignKey("contrats.id"))
    frais = Column(BigInteger, nullable=False)
    path = Column(String(255), nullable=False)
    statut = Column(Boolean, nullable=False)
    commentaire = Column(String(255), nullable=False)

    contrat = relationship("Contrat", back_populates="factures")

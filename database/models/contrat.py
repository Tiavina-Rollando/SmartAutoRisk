from sqlalchemy import Column, BigInteger, Date, Enum, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Contrat(Base):
    __tablename__ = "contrats"

    id = Column(BigInteger, primary_key=True)
    vehicule_id = Column(BigInteger, ForeignKey("vehicules.id"))
    date = Column(Date, nullable=False)
    path = Column(String(255), nullable=False)
    tarif = Column(Enum("simple", "prenium", name="tarif_enum"), default="simple")
    type_paiement = Column(
        Enum("annuel", "semestriel", "trimestriel", "mensuel", name="paiement_enum"),
        default="annuel"
    )

    vehicule = relationship("Vehicule", back_populates="contrats")
    factures = relationship("Facture", back_populates="contrat")

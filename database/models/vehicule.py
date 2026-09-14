from sqlalchemy import (
    Column, BigInteger, String, Enum, Integer, SmallInteger, ForeignKey, Float
)
from sqlalchemy.orm import relationship
from .base import Base

class Vehicule(Base):
    __tablename__ = "vehicules"

    id = Column(BigInteger, primary_key=True)
    marque = Column(String(255), nullable=False)
    modele = Column(String(255))
    puissance = Column(BigInteger, nullable=False)
    cylindre = Column(Float, nullable=True)
    type = Column(Enum("Voiture", "Moto", name="type_vehicule_enum"), default="Voiture")
    annee = Column(Integer, nullable=False)
    valeur = Column(BigInteger, nullable=False)
    usage = Column(Enum("Personnel", "Transport", name="usage_enum"), default="Personnel")
    nombre_place = Column(SmallInteger, nullable=False)
    immatriculation = Column(String(255))

    proprietaire_id = Column(BigInteger, ForeignKey("proprietaires.id"))

    proprietaire = relationship("Proprietaire", back_populates="vehicules")
    risques = relationship("HistoriqueNiveauRisk", back_populates="vehicule")
    contrats = relationship("Contrat", back_populates="vehicule")

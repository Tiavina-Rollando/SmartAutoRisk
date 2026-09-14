from sqlalchemy import Boolean, Column, BigInteger, String, Date, Enum
from sqlalchemy.orm import relationship
from .base import Base

class Proprietaire(Base):
    __tablename__ = "proprietaires"

    id = Column(BigInteger, primary_key=True)
    nom = Column(String(255), nullable=False)
    prenom = Column(String(255), nullable=False)
    sexe = Column(Boolean, nullable=False)
    date_permis = Column(Date, nullable=False)
    date_naissance = Column(Date, nullable=False)
    aptitude_conduite = Column(
        Enum("Normale", "Réduite", name="aptitude_enum"),
        default="Normale",
        nullable=False
    )
    adresse = Column(String(255))

    vehicules = relationship("Vehicule", back_populates="proprietaire")
    profils = relationship("HistoriqueProfil", back_populates="proprietaire")

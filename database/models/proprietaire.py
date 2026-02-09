from sqlalchemy import Column, BigInteger, String, Date, Enum
from sqlalchemy.orm import relationship
from .base import Base

class Proprietaire(Base):
    __tablename__ = "proprietaires"

    id = Column(BigInteger, primary_key=True)
    nom = Column(String(255), nullable=False)
    prenom = Column(String(255), nullable=False)
    date_permis = Column(Date, nullable=False)
    date_naissance = Column(Date, nullable=False)
    aptitude_conduite = Column(
        Enum("normale", "réduite", name="aptitude_enum"),
        default="normale",
        nullable=False
    )
    adresse = Column(String(255))

    vehicules = relationship("Vehicule", back_populates="proprietaire")

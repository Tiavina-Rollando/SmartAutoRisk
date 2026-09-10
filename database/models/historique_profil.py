from sqlalchemy import Column, BigInteger, Date, Enum, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class HistoriqueProfil(Base):
    __tablename__ = "historique_profils"

    id = Column(BigInteger, primary_key=True)
    proprietaire_id = Column(BigInteger, ForeignKey("proprietaires.id"))
    date_evaluation = Column(Date, nullable=False)
    profil = Column(
        Enum("Prudent", "Normal", "Risqué", name="profil_enum"),
        default="Normal"
    )
    source = Column(
        Enum("règle", "RNA", name="source_profil_enum"),
        default="règle"
    )

    proprietaire = relationship("Proprietaire", back_populates="profils")

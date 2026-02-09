from sqlalchemy import Column, BigInteger, Date, Enum, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class HistoriqueProfil(Base):
    __tablename__ = "historique_profils"

    id = Column(BigInteger, primary_key=True)
    vehicule_id = Column(BigInteger, ForeignKey("vehicules.id"))
    date_evaluation = Column(Date, nullable=False)
    profil = Column(
        Enum("prudent", "normal", "risqué", name="profil_enum"),
        default="normal"
    )
    source = Column(
        Enum("règle", "RNA", name="source_profil_enum"),
        default="règle"
    )

    vehicule = relationship("Vehicule", back_populates="profils")

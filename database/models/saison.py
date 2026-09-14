from sqlalchemy import Column, BigInteger, SmallInteger, Enum
from sqlalchemy.orm import relationship
from .base import Base

class Saison(Base):
    __tablename__ = "saisons"

    id = Column(BigInteger, primary_key=True)
    mois = Column(SmallInteger, nullable=False)
    periode = Column(
        Enum("Calme", "Fête", "Vacance", name="periode_enum"),
        default="Calme"
    )
    type = Column(
        Enum("Sec", "Pluvieux", name="type_saison_enum"),
        default="Sec"
    )

    risques = relationship("HistoriqueNiveauRisk", back_populates="saison")

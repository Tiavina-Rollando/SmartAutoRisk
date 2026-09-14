from sqlalchemy import BigInteger, Column, Enum, Boolean, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
from .accident import GraviteEnum  # <-- Importer la même enum


class AccidentVehicule(Base):
  __tablename__ = "accident_vehicules"

  id = Column(BigInteger, primary_key=True)
  accident_id = Column(
      BigInteger, ForeignKey("accidents.id"), nullable=False
  )
  vehicule_id = Column(BigInteger, ForeignKey("vehicules.id"), nullable=False)
  degat = Column(
      Enum(GraviteEnum), default=GraviteEnum.mineur, nullable=False
  )  # <-- Vérifier ici
  responsabilite = Column(Boolean, default=False)
  role = Column(String(50))
  valeur = Column(Integer, default=0)

  accident = relationship("Accident", back_populates="vehicules")
  vehicule = relationship("Vehicule")
from sqlalchemy import Column, BigInteger, Enum, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class AccidentVehicule(Base):
    __tablename__ = "accident_vehicules"

    id = Column(BigInteger, primary_key=True)
    accident_id = Column(BigInteger, ForeignKey("accidents.id"))
    vehicule_id = Column(BigInteger, ForeignKey("vehicules.id"))
    degat = Column(Enum("faible", "moyen", "élévé", name="degat_enum"), default="faible")
    responsabilite = Column(Boolean, nullable=False)
    role = Column(Enum("fautif", "victime", "tiers", name="role_enum"), default="fautif")
    valeur = Column(BigInteger)

    accident = relationship("Accident", back_populates="vehicules")
    vehicule = relationship("Vehicule")

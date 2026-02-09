from sqlalchemy import Column, BigInteger, String, Date, Enum
from sqlalchemy.orm import relationship
from .base import Base

class Accident(Base):
    __tablename__ = "accidents"

    id = Column(BigInteger, primary_key=True)
    date = Column(Date, nullable=False)
    lieu = Column(String(255), nullable=False)
    gravite = Column(Enum("mineur", "majeur", name="gravite_enum"), default="mineur")
    type = Column(Enum("matériel", "physique", name="type_accident_enum"), default="matériel")

    vehicules = relationship("AccidentVehicule", back_populates="accident")

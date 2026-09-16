import enum
from sqlalchemy import BigInteger, Column, Date, Enum, String
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.orm import relationship
from .base import Base


class GraviteEnum(enum.Enum):
    mineur = "Mineur"
    majeur = "Majeur"


class Accident(Base):
    __tablename__ = "accidents"

    id = Column(BigInteger, primary_key=True)
    date = Column(Date, nullable=False)
    lieu = Column(String(255), nullable=False)

    gravite = Column(
        Enum(GraviteEnum),
        default=GraviteEnum.mineur,
        nullable=False
    )

    type = Column(String(50), default="matériel")

    photo_path = Column(MEDIUMTEXT, nullable=True)

    vehicules = relationship(
        "AccidentVehicule",
        back_populates="accident"
    )
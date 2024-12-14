from sqlalchemy import Column, Float, Integer, String, Enum
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

class ObjectType(enum.Enum):
    GALAXY = "galaxy"
    NEBULA = "nebula"
    CLUSTER = "cluster"
    PLANETARY_NEBULA = "planetary_nebula"
    UNKNOWN = "unknown"

class DeepSpaceObject(Base):
    __tablename__ = "deep_space_objects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    catalog = Column(String, index=True, nullable=False)
    catalog_id = Column(String, index=True, nullable=False)
    ra = Column(Float, nullable=False)
    dec = Column(Float, nullable=False)
    diameter = Column(Float)
    type = Column(Enum(ObjectType), nullable=False, default=ObjectType.UNKNOWN)
    magnitude = Column(Float)
    distance = Column(Float)
    constellation = Column(String, index=True)

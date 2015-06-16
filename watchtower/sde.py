from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import BigInteger, Column, Float, ForeignKey, Integer, String, Text


Base = declarative_base()


class MapDenormalize(Base):
    __tablename__ = "mapDenormalize"

    itemID = Column(BigInteger, primary_key=True)
    typeID = Column(BigInteger)
    groupID = Column(BigInteger)
    solarSystemID = Column(BigInteger)
    constellationID = Column(BigInteger)
    regionID = Column(BigInteger)
    orbitID = Column(BigInteger)
    x = Column(Float)
    y = Column(Float)
    z = Column(Float)
    radius = Column(Float)
    itemName = Column(Text)
    security = Column(Float)
    celestialIndex = Column(BigInteger)
    orbitIndex = Column(BigInteger)

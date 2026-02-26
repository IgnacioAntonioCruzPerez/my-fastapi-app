"""SQLAlchemy models for Organizations, Buildings, and Activities directory."""
from sqlalchemy import Column, Integer, String, ForeignKey, Float, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# Many-to-many: Organization <-> Activity
organization_activities = Table(
    "organization_activities",
    Base.metadata,
    Column("organization_id", Integer, ForeignKey("organizations.id"), primary_key=True),
    Column("activity_id", Integer, ForeignKey("activities.id"), primary_key=True),
)


class Building(Base):
    """Building with address and geographical coordinates."""

    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String(512), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    organizations = relationship("Organization", back_populates="building")


class Activity(Base):
    """Activity type with tree structure (max 3 levels)."""

    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256), nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("activities.id"), nullable=True)
    level = Column(Integer, nullable=False)  # 1, 2, or 3

    parent = relationship("Activity", remote_side=[id], backref="children")
    organizations = relationship(
        "Organization", secondary=organization_activities, back_populates="activities"
    )


class Organization(Base):
    """Organization card: name, phones, building, activities."""

    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256), nullable=False, index=True)
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=False)

    building = relationship("Building", back_populates="organizations")
    activities = relationship(
        "Activity", secondary=organization_activities, back_populates="organizations"
    )
    phones = relationship("OrganizationPhone", back_populates="organization", cascade="all, delete-orphan")


class OrganizationPhone(Base):
    """Phone number for an organization (one org can have many phones)."""

    __tablename__ = "organization_phones"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    phone_number = Column(String(64), nullable=False)

    organization = relationship("Organization", back_populates="phones")

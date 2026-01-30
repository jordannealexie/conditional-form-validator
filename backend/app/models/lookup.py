"""
Lookup tables for ABAC policy builder
These tables provide dynamic values for dropdowns in the UI
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.base_class import Base


class Department(Base):
    """Department lookup table for ABAC policies"""
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    code = Column(String(20), unique=True, nullable=True)  # Short code like "IT", "HR", "FIN"
    description = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    display_order = Column(Integer, default=0)  # For sorting in dropdowns
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Location(Base):
    """Location lookup table for ABAC policies"""
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    code = Column(String(20), unique=True, nullable=True)  # Short code like "MNL", "MKT", "QC"
    description = Column(String(255), nullable=True)
    region = Column(String(100), nullable=True)  # For grouping locations
    is_active = Column(Boolean, default=True, nullable=False)
    display_order = Column(Integer, default=0)  # For sorting in dropdowns
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

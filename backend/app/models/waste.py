"""
Waste Management Models

SQLAlchemy models for tracking waste in products and stores.
Provides waste recording, metrics aggregation, and trend analysis.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


class WasteRecord(Base):
    """Individual waste record for tracking specific waste events.
    
    Attributes:
        id: Primary key, auto-incremented integer
        product_id: Foreign key to products table
        store_id: Foreign key to stores table
        quantity_wasted: Amount of product wasted
        cost_wasted: Monetary value of wasted product
        waste_reason: Reason for waste (expired, damaged, theft, etc.)
        recorded_at: Timestamp when waste was recorded
        created_at: Timestamp of record creation
        updated_at: Timestamp of last update
    """
    
    __tablename__ = "waste_records"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    store_id = Column(
        Integer,
        ForeignKey("stores.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    quantity_wasted = Column(Float, nullable=False)
    cost_wasted = Column(Float, nullable=False)
    waste_reason = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    recorded_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    product = relationship("Product", back_populates="waste_records")
    store = relationship("Store", back_populates="waste_records")
    
    # Indexes for common queries
    __table_args__ = (
        Index("ix_waste_records_product_store", "product_id", "store_id"),
        Index("ix_waste_records_recorded_at", "recorded_at"),
        Index("ix_waste_records_store_recorded", "store_id", "recorded_at"),
    )
    
    def __repr__(self) -> str:
        return f"<WasteRecord(id={self.id}, product_id={self.product_id}, store_id={self.store_id}, quantity={self.quantity_wasted})>"


class WasteMetric(Base):
    """Aggregated daily waste metrics per product and store.
    
    Attributes:
        id: Primary key, auto-incremented integer
        product_id: Foreign key to products table
        store_id: Foreign key to stores table
        date: Date for the aggregated metrics
        total_quantity_wasted: Total quantity wasted that day
        total_cost_wasted: Total cost wasted that day
        record_count: Number of individual waste records
        created_at: Timestamp of record creation
        updated_at: Timestamp of last update
    """
    
    __tablename__ = "waste_metrics"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    store_id = Column(
        Integer,
        ForeignKey("stores.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    date = Column(DateTime, nullable=False, index=True)
    total_quantity_wasted = Column(Float, nullable=False, default=0.0)
    total_cost_wasted = Column(Float, nullable=False, default=0.0)
    record_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    product = relationship("Product", back_populates="waste_metrics")
    store = relationship("Store", back_populates="waste_metrics")
    
    # Indexes
    __table_args__ = (
        Index("ix_waste_metrics_product_date", "product_id", "date"),
        Index("ix_waste_metrics_store_date", "store_id", "date"),
        Index("ix_waste_metrics_unique", "product_id", "store_id", "date", unique=True),
    )
    
    def __repr__(self) -> str:
        return f"<WasteMetric(id={self.id}, product_id={self.product_id}, date={self.date}, cost={self.total_cost_wasted})>"


class Product(Base):
    """Product catalog for items that can have waste tracking.
    
    Attributes:
        id: Primary key, auto-incremented integer
        sku: Unique product SKU
        name: Product name
        category: Product category
        unit_of_measure: Unit (kg, units, liters, etc.)
        cost_price: Cost price per unit
        sell_price: Selling price per unit
        shelf_life_days: Expected shelf life in days
        is_active: Whether product is active
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
    """
    
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sku = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=True, index=True)
    unit_of_measure = Column(String(20), nullable=False, default="units")
    cost_price = Column(Float, nullable=False, default=0.0)
    sell_price = Column(Float, nullable=False, default=0.0)
    shelf_life_days = Column(Integer, nullable=True)
    is_active = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    waste_records = relationship("WasteRecord", back_populates="product")
    waste_metrics = relationship("WasteMetric", back_populates="product")
    alerts = relationship("Alert", back_populates="product")
    demand_predictions = relationship("DemandPrediction", back_populates="product")
    inventory = relationship("InventoryStore", back_populates="product")
    
    def __repr__(self) -> str:
        return f"<Product(id={self.id}, sku='{self.sku}', name='{self.name}')>"


class Store(Base):
    """Store/location for waste tracking.
    
    Attributes:
        id: Primary key, auto-incremented integer
        store_code: Unique store code
        name: Store name
        address: Store address
        region: Geographic region
        is_active: Whether store is active
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
    """
    
    __tablename__ = "stores"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    store_code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    address = Column(String(500), nullable=True)
    region = Column(String(100), nullable=True, index=True)
    is_active = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    waste_records = relationship("WasteRecord", back_populates="store")
    waste_metrics = relationship("WasteMetric", back_populates="store")
    alerts = relationship("Alert", back_populates="store")
    demand_predictions = relationship("DemandPrediction", back_populates="store")
    inventory = relationship("InventoryStore", back_populates="store")
    
    def __repr__(self) -> str:
        return f"<Store(id={self.id}, store_code='{self.store_code}', name='{self.name}')>"

"""
Demand Prediction Models

SQLAlchemy models for tracking demand predictions and forecasts.
Provides demand forecasting by product, store, and date.
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
)
from sqlalchemy.orm import relationship

from app.db.base import Base


class DemandPrediction(Base):
    """Demand prediction model for storing forecast results.
    
    Attributes:
        id: Primary key, auto-incremented integer
        product_id: Foreign key to products table
        store_id: Foreign key to stores table
        predicted_demand: Forecasted demand quantity
        prediction_date: Date for which prediction is made
        confidence_level: Confidence level of prediction (0-1)
        model_version: Version of prediction model used
        prediction_type: Type of prediction (daily, weekly, seasonal)
        created_at: Timestamp when prediction was generated
    """
    
    __tablename__ = "demand_predictions"
    
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
    predicted_demand = Column(Float, nullable=False)
    prediction_date = Column(DateTime, nullable=False, index=True)
    confidence_level = Column(Float, nullable=True)
    model_version = Column(String(50), nullable=True)
    prediction_type = Column(String(50), nullable=False, default="daily")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    product = relationship("Product", back_populates="demand_predictions")
    store = relationship("Store", back_populates="demand_predictions")
    
    # Indexes for common query patterns
    __table_args__ = (
        Index("ix_demand_predictions_product_date", "product_id", "prediction_date"),
        Index("ix_demand_predictions_store_date", "store_id", "prediction_date"),
        Index("ix_demand_predictions_product_store_date", "product_id", "store_id", "prediction_date"),
    )
    
    def __repr__(self) -> str:
        return f"<DemandPrediction(id={self.id}, product_id={self.product_id}, predicted_demand={self.predicted_demand})>"

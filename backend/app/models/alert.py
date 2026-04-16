"""
Alert Management Models

SQLAlchemy models for tracking alerts in the waste optimization system.
Provides alert generation, classification, and lifecycle management.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


class Alert(Base):
    """Alert model for tracking system alerts and notifications.
    
    Attributes:
        id: Primary key, auto-incremented integer
        product_id: Optional foreign key to products table
        store_id: Optional foreign key to stores table
        severity: Alert severity level (info, warning, critical)
        alert_type: Type of alert (overstock, waste_risk, low_stock, etc.)
        message: Alert message/descriptio
        created_at: Timestamp when alert was generated
        acknowledged_at: Timestamp when alert was acknowledged
        resolved_at: Timestamp when alert was resolved
        is_active: Boolean flag indicating if alert is still active
    """
    
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True,
        index=True,
    )
    store_id = Column(
        Integer,
        ForeignKey("stores.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True,
        index=True,
    )
    severity = Column(String(20), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False, index=True)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    is_active = Column(Integer, default=1, nullable=False, index=True)
    
    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_alerts_severity_created', 'severity', 'created_at'),
        Index('idx_alerts_product_store', 'product_id', 'store_id'),
        Index('idx_alerts_active_severity', 'is_active', 'severity'),
    )
    
    # Relationships
    product = relationship("Product", back_populates="alerts")
    store = relationship("Store", back_populates="alerts")
    
    def __repr__(self) -> str:
        return f"<Alert(id={self.id}, severity='{self.severity}', type='{self.alert_type}', is_active={self.is_active})>"
    
    @property
    def is_critical(self) -> bool:
        """Check if alert is critical severity."""
        return self.severity == "critical"
    
    @property
    def is_warning(self) -> bool:
        """Check if alert is warning severity."""
        return self.severity == "warning"
    
    @property
    def is_info(self) -> bool:
        """Check if alert is info severity."""
        return self.severity == "info"
    
    def acknowledge(self) -> None:
        """Mark alert as acknowledged."""
        self.acknowledged_at = datetime.utcnow()
    
    def resolve(self) -> None:
        """Mark alert as resolved."""
        self.resolved_at = datetime.utcnow()
        self.is_active = 0
    
    def to_dict(self) -> dict:
        """Convert alert to dictionary representation."""
        return {
            "id": self.id,
            "product_id": self.product_id,
            "store_id": self.store_id,
            "severity": self.severity,
            "alert_type": self.alert_type,
            "message": self.message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "is_active": bool(self.is_active),
        }

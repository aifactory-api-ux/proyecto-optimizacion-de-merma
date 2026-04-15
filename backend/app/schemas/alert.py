"""
Alert Schemas

Pydantic models for alert responses and data transfer.
Provides request/response schemas for alert management endpoints.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AlertResponse(BaseModel):
    """Response model for alert data.
    
    Attributes:
        id: Unique identifier of the alert
        created_at: Timestamp when alert was generated
        message: Alert message/description
        severity: Alert severity level (info, warning, critical)
    """
    id: int = Field(
        ...,
        description="Unique identifier of the alert",
        examples=[1]
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when alert was generated",
        examples=["2026-04-15T10:30:00"]
    )
    message: str = Field(
        ...,
        description="Alert message or description",
        examples=["High waste detected for product Leche Entera 1L in Store 1"]
    )
    severity: str = Field(
        ...,
        description="Alert severity level",
        examples=["warning"],
        pattern="^(info|warning|critical)$"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "created_at": "2026-04-15T10:30:00",
                "message": "High waste detected for product Leche Entera 1L in Store 1",
                "severity": "warning"
            }
        }


class AlertCreate(BaseModel):
    """Request model for creating a new alert.
    
    Attributes:
        product_id: Optional product identifier linked to the alert
        store_id: Optional store identifier linked to the alert
        severity: Alert severity level (info, warning, critical)
        alert_type: Type of alert (overstock, waste_risk, low_stock, etc.)
        message: Alert message/description
    """
    product_id: Optional[int] = Field(
        default=None,
        description="Optional product identifier linked to the alert",
        examples=[1]
    )
    store_id: Optional[int] = Field(
        default=None,
        description="Optional store identifier linked to the alert",
        examples=[1]
    )
    severity: str = Field(
        ...,
        description="Alert severity level",
        examples=["warning"],
        pattern="^(info|warning|critical)$"
    )
    alert_type: str = Field(
        ...,
        description="Type of alert",
        examples=["waste_risk"]
    )
    message: str = Field(
        ...,
        description="Alert message or description",
        min_length=1,
        max_length=1000,
        examples=["High waste detected for product Leche Entera 1L in Store 1"]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "product_id": 1,
                "store_id": 1,
                "severity": "warning",
                "alert_type": "waste_risk",
                "message": "High waste detected for product Leche Entera 1L in Store 1"
            }
        }


class AlertUpdate(BaseModel):
    """Request model for updating an existing alert.
    
    Attributes:
        acknowledged_at: Timestamp when alert was acknowledged
        resolved_at: Timestamp when alert was resolved
        is_active: Boolean flag indicating if alert is still active
    """
    acknowledged_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when alert was acknowledged"
    )
    resolved_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when alert was resolved"
    )
    is_active: Optional[bool] = Field(
        default=None,
        description="Boolean flag indicating if alert is still active"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "acknowledged_at": "2026-04-15T11:00:00",
                "resolved_at": None,
                "is_active": True
            }
        }

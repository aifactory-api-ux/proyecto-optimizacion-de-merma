"""
Dashboard Schemas

Pydantic models for dashboard metrics and visualization.
Provides response schemas for consolidated waste metrics, trends, and predictions.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class WasteMetric(BaseModel):
    """Waste metric data point for dashboard display.
    
    Attributes:
        date: Date of the waste record
        product_id: Unique identifier of the product
        product_name: Name of the product
        waste_quantity: Amount of product wasted
        waste_cost: Monetary value of the wasted product
    """
    date: datetime = Field(
        ...,
        description="Date of the waste record",
        examples=["2026-04-15T00:00:00"]
    )
    product_id: int = Field(
        ...,
        description="Unique identifier of the product",
        examples=[1]
    )
    product_name: str = Field(
        ...,
        description="Name of the product",
        examples=["Leche Entera 1L"]
    )
    waste_quantity: float = Field(
        ...,
        description="Amount of product wasted",
        ge=0,
        examples=[5.5]
    )
    waste_cost: float = Field(
        ...,
        description="Monetary value of the wasted product",
        ge=0,
        examples=[55.50]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "date": "2026-04-15T00:00:00",
                "product_id": 1,
                "product_name": "Leche Entera 1L",
                "waste_quantity": 5.5,
                "waste_cost": 55.50
            }
        }


class DashboardMetricsResponse(BaseModel):
    """Response model for dashboard metrics endpoint.
    
    Provides consolidated waste metrics including totals, breakdowns by product,
    time trends, active alerts, and demand predictions.
    
    Attributes:
        total_waste_quantity: Total quantity of waste across all products
        total_waste_cost: Total monetary value of waste
        waste_by_product: List of waste metrics grouped by product
        waste_trend: Time series of waste metrics for trend analysis
        alerts: List of active alert messages
        demand_prediction: Optional predicted demand value
    """
    total_waste_quantity: float = Field(
        ...,
        description="Total quantity of waste across all products",
        ge=0,
        examples=[125.5]
    )
    total_waste_cost: float = Field(
        ...,
        description="Total monetary value of waste",
        ge=0,
        examples=[1255.75]
    )
    waste_by_product: List[WasteMetric] = Field(
        default_factory=list,
        description="List of waste metrics grouped by product"
    )
    waste_trend: List[WasteMetric] = Field(
        default_factory=list,
        description="Time series of waste metrics for trend analysis"
    )
    alerts: List[str] = Field(
        default_factory=list,
        description="List of active alert messages"
    )
    demand_prediction: Optional[float] = Field(
        default=None,
        description="Optional predicted demand value",
        examples=[45.0]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "total_waste_quantity": 125.5,
                "total_waste_cost": 1255.75,
                "waste_by_product": [
                    {
                        "date": "2026-04-15T00:00:00",
                        "product_id": 1,
                        "product_name": "Leche Entera 1L",
                        "waste_quantity": 5.5,
                        "waste_cost": 55.50
                    }
                ],
                "waste_trend": [
                    {
                        "date": "2026-04-15T00:00:00",
                        "product_id": 1,
                        "product_name": "Leche Entera 1L",
                        "waste_quantity": 5.5,
                        "waste_cost": 55.50
                    }
                ],
                "alerts": [
                    "High waste detected for product Leche Entera 1L",
                    "Overstock risk in Store 1"
                ],
                "demand_prediction": 45.0
            }
        }

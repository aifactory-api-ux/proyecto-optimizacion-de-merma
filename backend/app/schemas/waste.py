"""
Waste Schemas

Pydantic models for waste-related API requests and responses.
Provides request/response schemas for waste metrics, trends, and filtering.
"""

from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, Field


class WasteQueryParams(BaseModel):
    """Query parameters for waste data retrieval.
    
    Attributes:
        start_date: Start date for filtering waste records (ISO 8601)
        end_date: End date for filtering waste records (ISO 8601)
        product_id: Optional product ID for filtering by specific product
        store_id: Optional store ID for filtering by specific store
    """
    start_date: datetime = Field(
        ...,
        description="Start date for filtering waste records",
        examples=["2026-01-01T00:00:00"]
    )
    end_date: datetime = Field(
        ...,
        description="End date for filtering waste records",
        examples=["2026-04-15T23:59:59"]
    )
    product_id: Optional[int] = Field(
        default=None,
        description="Optional product ID to filter results",
        examples=[1]
    )
    store_id: Optional[int] = Field(
        default=None,
        description="Optional store ID to filter results",
        examples=[1]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "start_date": "2026-01-01T00:00:00",
                "end_date": "2026-04-15T23:59:59",
                "product_id": 1,
                "store_id": 1
            }
        }


class WasteByProductResponse(BaseModel):
    """Response model for waste by product aggregation.
    
    Attributes:
        date: Date of the waste record
        product_id: Unique identifier of the product
        product_name: Name of the product
        waste_quantity: Total amount of product wasted
        waste_cost: Total monetary value of waste
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
        description="Total amount of product wasted",
        ge=0,
        examples=[150.5]
    )
    waste_cost: float = Field(
        ...,
        description="Total monetary value of wasted products",
        ge=0,
        examples=[1505.00]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "date": "2026-04-15T00:00:00",
                "product_id": 1,
                "product_name": "Leche Entera 1L",
                "waste_quantity": 150.5,
                "waste_cost": 1505.00
            }
        }


class WasteTrendResponse(BaseModel):
    """Response model for waste trend data points.
    
    Attributes:
        date: Date of the waste record
        product_id: Unique identifier of the product
        product_name: Name of the product
        waste_quantity: Amount of product wasted on this date
        waste_cost: Monetary value of waste on this date
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


class WasteSummaryResponse(BaseModel):
    """Response model for waste summary aggregation.
    
    Attributes:
        total_waste_quantity: Total quantity wasted in the period
        total_waste_cost: Total cost of waste in the period
        unique_products: Number of unique products
        unique_stores: Number of unique stores
        total_records: Total number of waste records
        avg_daily_quantity: Average daily waste quantity
        avg_daily_cost: Average daily waste cost
        start_date: Start date of the reporting period
        end_date: End date of the reporting period
    """
    total_waste_quantity: float = Field(
        ...,
        description="Total quantity wasted in the period",
        ge=0,
        examples=[1500.0]
    )
    total_waste_cost: float = Field(
        ...,
        description="Total cost of waste in the period",
        ge=0,
        examples=[15000.00]
    )
    unique_products: int = Field(
        ...,
        description="Number of unique products with waste",
        ge=0,
        examples=[25]
    )
    unique_stores: int = Field(
        ...,
        description="Number of unique stores with waste",
        ge=0,
        examples=[3]
    )
    total_records: int = Field(
        ...,
        description="Total number of waste records",
        ge=0,
        examples=[150]
    )
    avg_daily_quantity: float = Field(
        ...,
        description="Average daily waste quantity",
        ge=0,
        examples=[50.0]
    )
    avg_daily_cost: float = Field(
        ...,
        description="Average daily waste cost",
        ge=0,
        examples=[500.00]
    )
    start_date: str = Field(
        ...,
        description="Start date of the reporting period"
    )
    end_date: str = Field(
        ...,
        description="End date of the reporting period"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "total_waste_quantity": 1500.0,
                "total_waste_cost": 15000.00,
                "unique_products": 25,
                "unique_stores": 3,
                "total_records": 150,
                "avg_daily_quantity": 50.0,
                "avg_daily_cost": 500.00,
                "start_date": "2026-01-01T00:00:00",
                "end_date": "2026-04-15T23:59:59"
            }
        }


class CreateWasteRecordRequest(BaseModel):
    """Request model for creating a new waste record.
    
    Attributes:
        product_id: Foreign key to the product being wasted
        store_id: Foreign key to the store where waste occurred
        quantity_wasted: Amount of product wasted
        cost_wasted: Monetary value of wasted product
        waste_reason: Reason for waste (expired, damaged, theft, etc.)
        notes: Optional additional notes
        recorded_at: Timestamp when the waste occurred
    """
    product_id: int = Field(
        ...,
        description="Foreign key to the product",
        examples=[1]
    )
    store_id: int = Field(
        ...,
        description="Foreign key to the store",
        examples=[1]
    )
    quantity_wasted: float = Field(
        ...,
        description="Amount of product wasted",
        gt=0,
        examples=[5.5]
    )
    cost_wasted: float = Field(
        ...,
        description="Monetary value of wasted product",
        ge=0,
        examples=[55.50]
    )
    waste_reason: Optional[str] = Field(
        default=None,
        description="Reason for waste",
        max_length=100,
        examples=["expired"]
    )
    notes: Optional[str] = Field(
        default=None,
        description="Optional additional notes",
        max_length=500
    )
    recorded_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when the waste occurred"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "product_id": 1,
                "store_id": 1,
                "quantity_wasted": 5.5,
                "cost_wasted": 55.50,
                "waste_reason": "expired",
                "notes": "Product past expiration date",
                "recorded_at": "2026-04-15T10:30:00"
            }
        }


class UpdateWasteRecordRequest(BaseModel):
    """Request model for updating an existing waste record.
    
    Attributes:
        quantity_wasted: Updated amount of product wasted
        cost_wasted: Updated monetary value of wasted product
        waste_reason: Updated reason for waste
        notes: Updated additional notes
    """
    quantity_wasted: Optional[float] = Field(
        default=None,
        description="Updated amount of product wasted",
        gt=0
    )
    cost_wasted: Optional[float] = Field(
        default=None,
        description="Updated monetary value of wasted product",
        ge=0
    )
    waste_reason: Optional[str] = Field(
        default=None,
        description="Updated reason for waste",
        max_length=100
    )
    notes: Optional[str] = Field(
        default=None,
        description="Updated additional notes",
        max_length=500
    )

    class Config:
        json_schema_extra = {
            "example": {
                "quantity_wasted": 3.0,
                "cost_wasted": 30.00,
                "waste_reason": "damaged",
                "notes": "Packaging damage during handling"
            }
        }


class WasteRecordResponse(BaseModel):
    """Response model for single waste record retrieval.
    
    Attributes:
        id: Unique identifier of the waste record
        product_id: Foreign key to the product
        store_id: Foreign key to the store
        quantity_wasted: Amount of product wasted
        cost_wasted: Monetary value of wasted product
        waste_reason: Reason for waste
        notes: Additional notes
        recorded_at: Timestamp when the waste occurred
        created_at: Timestamp when the record was created
        updated_at: Timestamp when the record was last updated
    """
    id: int = Field(
        ...,
        description="Unique identifier of the waste record"
    )
    product_id: int = Field(
        ...,
        description="Foreign key to the product"
    )
    store_id: int = Field(
        ...,
        description="Foreign key to the store"
    )
    quantity_wasted: float = Field(
        ...,
        description="Amount of product wasted"
    )
    cost_wasted: float = Field(
        ...,
        description="Monetary value of wasted product"
    )
    waste_reason: Optional[str] = Field(
        default=None,
        description="Reason for waste"
    )
    notes: Optional[str] = Field(
        default=None,
        description="Additional notes"
    )
    recorded_at: str = Field(
        ...,
        description="Timestamp when the waste occurred"
    )
    created_at: Optional[str] = Field(
        default=None,
        description="Timestamp when the record was created"
    )
    updated_at: Optional[str] = Field(
        default=None,
        description="Timestamp when the record was last updated"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "product_id": 1,
                "store_id": 1,
                "quantity_wasted": 5.5,
                "cost_wasted": 55.50,
                "waste_reason": "expired",
                "notes": "Product past expiration date",
                "recorded_at": "2026-04-15T10:30:00",
                "created_at": "2026-04-15T10:35:00",
                "updated_at": "2026-04-15T10:35:00"
            }
        }

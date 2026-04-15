"""
Demand Prediction Schemas

Pydantic models for demand prediction requests and responses.
Provides request/response schemas for forecasting endpoints.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DemandPredictionRequest(BaseModel):
    """Request model for getting demand predictions.
    
    Attributes:
        product_id: Unique identifier of the product to predict
        date: Date for which to make the prediction (ISO 8601 format)
    """
    product_id: int = Field(
        ...,
        description="Unique identifier of the product",
        gt=0,
        examples=[1]
    )
    date: str = Field(
        ...,
        description="Date for prediction in ISO 8601 format",
        examples=["2026-04-15"]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "product_id": 1,
                "date": "2026-04-15"
            }
        }


class DemandPredictionResponse(BaseModel):
    """Response model for demand prediction endpoint.
    
    Attributes:
        demand_prediction: Forecasted demand quantity for the product
    """
    demand_prediction: float = Field(
        ...,
        description="Forecasted demand quantity",
        ge=0,
        examples=[15.5]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "demand_prediction": 15.5
            }
        }


class DemandPredictionDetail(BaseModel):
    """Detailed response model for demand predictions with metadata.
    
    Attributes:
        product_id: Unique identifier of the product
        store_id: Unique identifier of the store
        predicted_demand: Forecasted demand quantity
        prediction_date: Date for which prediction was made
        confidence_level: Confidence level of prediction (0-1)
        model_version: Version of prediction model used
        prediction_type: Type of prediction (daily, weekly, seasonal)
        created_at: Timestamp when prediction was generated
    """
    product_id: int = Field(
        ...,
        description="Unique identifier of the product",
        examples=[1]
    )
    store_id: int = Field(
        ...,
        description="Unique identifier of the store",
        examples=[1]
    )
    predicted_demand: float = Field(
        ...,
        description="Forecasted demand quantity",
        ge=0,
        examples=[15.5]
    )
    prediction_date: datetime = Field(
        ...,
        description="Date for which prediction was made",
        examples=["2026-04-15T00:00:00"]
    )
    confidence_level: Optional[float] = Field(
        default=None,
        description="Confidence level of prediction (0-1)",
        ge=0,
        le=1,
        examples=[0.85]
    )
    model_version: Optional[str] = Field(
        default=None,
        description="Version of prediction model used",
        examples=["v1.0.0"]
    )
    prediction_type: str = Field(
        default="daily",
        description="Type of prediction",
        examples=["daily"]
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when prediction was generated",
        examples=["2026-04-15T08:00:00"]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "product_id": 1,
                "store_id": 1,
                "predicted_demand": 15.5,
                "prediction_date": "2026-04-15T00:00:00",
                "confidence_level": 0.85,
                "model_version": "v1.0.0",
                "prediction_type": "daily",
                "created_at": "2026-04-15T08:00:00"
            }
        }

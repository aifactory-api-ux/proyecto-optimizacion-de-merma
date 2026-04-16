"""
Demand Prediction API Endpoints

REST API endpoints for demand prediction functionality.
Provides demand forecasting and recommendations for products.
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.security import verify_token_and_get_user_id
from app.db.session import get_db
from app.schemas.demand import (
    DemandPredictionRequest,
    DemandPredictionResponse,
    DemandPredictionDetail,
)
from app.services.demand_service import DemandService
from shared.constants import ERROR_MESSAGES, HTTP_STATUS

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/demand", tags=["demand"])


def get_current_user_id_from_token(
    token: str = Depends(lambda: None)
) -> int:
    """Dependency to extract user ID from JWT token.
    
    This is a placeholder - actual implementation uses FastAPI dependency
    with proper OAuth2 bearer token parsing.
    """
    pass


def require_auth(authorization: str = Query(None, alias="Authorization")) -> int:
    """Extract and validate user ID from Authorization header."""
    if not authorization:
        raise HTTPException(status_code=HTTP_STATUS["UNAUTHORIZED"], detail=ERROR_MESSAGES["UNAUTHORIZED"])
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=HTTP_STATUS["UNAUTHORIZED"], detail="Invalid authorization header format")
    token = parts[1]
    user_id = verify_token_and_get_user_id(token)
    if user_id is None:
        raise HTTPException(status_code=HTTP_STATUS["UNAUTHORIZED"], detail=ERROR_MESSAGES["UNAUTHORIZED"])
    return user_id


@router.get("/prediction", response_model=DemandPredictionResponse)
async def get_demand_prediction(
    product_id: int = Query(..., description="Product ID for prediction", ge=1),
    date: str = Query(..., description="Date for prediction in ISO 8601 format"),
    db: Session = Depends(get_db),
    authorization: str = Query(None, alias="Authorization"),
) -> DemandPredictionResponse:
    """Get demand prediction for a product on a given date.
    
    Args:
        product_id: The unique identifier of the product
        date: The date for which to get prediction (ISO 8601 format)
        db: Database session
        authorization: Bearer token for authentication
    
    Returns:
        DemandPredictionResponse: Object containing the demand prediction value
    
    Raises:
        HTTPException: If authentication fails or prediction not found
    """
    if not authorization:
        raise HTTPException(
            status_code=HTTP_STATUS["UNAUTHORIZED"],
            detail=ERROR_MESSAGES["UNAUTHORIZED"],
        )
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=HTTP_STATUS["UNAUTHORIZED"],
            detail="Invalid authorization header format",
        )
    
    token = parts[1]
    user_id = verify_token_and_get_user_id(token)
    if user_id is None:
        raise HTTPException(
            status_code=HTTP_STATUS["UNAUTHORIZED"],
            detail=ERROR_MESSAGES["UNAUTHORIZED"],
        )
    
    # Parse the date parameter
    try:
        prediction_date = datetime.fromisoformat(date.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=HTTP_STATUS["BAD_REQUEST"],
            detail=ERROR_MESSAGES["INVALID_FORMAT"].format("date"),
        )
    
    # Get demand prediction from service
    demand_service = DemandService(db)
    
    try:
        prediction = demand_service.get_prediction_for_product_date(
            product_id=product_id,
            prediction_date=prediction_date,
        )
        
        if prediction is None:
            # If no stored prediction, generate a new one
            prediction = demand_service.generate_prediction(
                product_id=product_id,
                prediction_date=prediction_date,
            )
            
            if prediction is None:
                raise HTTPException(
                    status_code=HTTP_STATUS["NOT_FOUND"],
                    detail=ERROR_MESSAGES["NOT_FOUND"].format("Demand prediction"),
                )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving demand prediction: {e}")
        raise HTTPException(
            status_code=HTTP_STATUS["INTERNAL_ERROR"],
            detail=ERROR_MESSAGES["INTERNAL_ERROR"],
        )
    
    return DemandPredictionResponse(demand_prediction=prediction)


@router.post("/prediction", response_model=DemandPredictionDetail)
async def create_demand_prediction(
    request: DemandPredictionRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(require_auth),
) -> DemandPredictionDetail:
    
    demand_service = DemandService(db)
    
    try:
        prediction = demand_service.create_prediction(
            product_id=request.product_id,
            store_id=request.store_id,
            predicted_demand=request.predicted_demand,
            prediction_date=request.prediction_date,
            confidence_level=request.confidence_level,
            model_version=request.model_version,
            prediction_type=request.prediction_type,
        )
    except Exception as e:
        logger.error(f"Error creating demand prediction: {e}")
        raise HTTPException(
            status_code=HTTP_STATUS["INTERNAL_ERROR"],
            detail=ERROR_MESSAGES["INTERNAL_ERROR"],
        )
    
    return prediction


@router.get("/forecast/{product_id}", response_model=list[DemandPredictionDetail])
async def get_forecast(
    product_id: int,
    start_date: str = Query(..., description="Start date in ISO 8601 format"),
    end_date: str = Query(..., description="End date in ISO 8601 format"),
    store_id: Optional[int] = Query(None, description="Optional store ID filter"),
    db: Session = Depends(get_db),
    user_id: int = Depends(require_auth),
) -> list[DemandPredictionDetail]:
    
    # Parse dates
    try:
        start = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
        end = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=HTTP_STATUS["BAD_REQUEST"],
            detail=ERROR_MESSAGES["INVALID_FORMAT"].format("date"),
        )
    
    demand_service = DemandService(db)
    
    try:
        predictions = demand_service.get_forecast_range(
            product_id=product_id,
            start_date=start,
            end_date=end,
            store_id=store_id,
        )
    except Exception as e:
        logger.error(f"Error retrieving forecast: {e}")
        raise HTTPException(
            status_code=HTTP_STATUS["INTERNAL_ERROR"],
            detail=ERROR_MESSAGES["INTERNAL_ERROR"],
        )
    
    return predictions


@router.get("/recommendations/{product_id}", response_model=dict)
async def get_recommendations(
    product_id: int,
    store_id: Optional[int] = Query(None, description="Store ID"),
    db: Session = Depends(get_db),
    token: str = Depends(verify_token_and_get_user_id),
) -> dict:
    """Get inventory recommendations for a product.
    
    Based on demand prediction and current inventory levels,
    provides recommendations for reorder, discount, or no action.
    
    Args:
        product_id: The unique identifier of the product
        store_id: Optional store ID (uses default if not provided)
        db: Database session
        token: JWT authentication token
    
    Returns:
        Dictionary containing recommendation and reasoning
    """
    user_id = verify_token_and_get_user_id(token) if token else None
    if user_id is None:
        raise HTTPException(
            status_code=HTTP_STATUS["UNAUTHORIZED"],
            detail=ERROR_MESSAGES["UNAUTHORIZED"],
        )
    
    demand_service = DemandService(db)
    
    try:
        recommendation = demand_service.get_inventory_recommendation(
            product_id=product_id,
            store_id=store_id,
        )
    except Exception as e:
        logger.error(f"Error generating recommendation: {e}")
        raise HTTPException(
            status_code=HTTP_STATUS["INTERNAL_ERROR"],
            detail=ERROR_MESSAGES["INTERNAL_ERROR"],
        )
    
    return recommendation

"""
Waste Management API Endpoints

Provides REST API endpoints for waste tracking, querying, and reporting.
Implements time series queries, waste by product, and trend analysis.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_


from app.core.config import settings
from app.core.security import verify_token_and_get_user_id
from app.db.session import get_db
from app.models.waste import WasteRecord, WasteMetric, Product, Store
from app.schemas.waste import (
    WasteQueryParams,
    WasteByProductResponse,
    WasteTrendResponse,
    WasteSummaryResponse,
    CreateWasteRecordRequest,
    UpdateWasteRecordRequest,
    WasteRecordResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/waste", tags=["waste"])


def get_current_user_id_from_token(
    authorization: str = Depends(lambda: None)
) -> int:
    """Extract and validate user ID from authorization token.
    
    Args:
        authorization: Authorization header with Bearer token
        
    Returns:
        User ID from token
        
    Raises:
        HTTPException: If token is invalid or missing
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = verify_token_and_get_user_id(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id


def validate_date_range(start_date: str, end_date: str) -> tuple:
    """Validate and parse date range parameters.
    
    Args:
        start_date: Start date in ISO 8601 format
        end_date: End date in ISO 8601 format
        
    Returns:
        Tuple of (start_datetime, end_datetime)
        
    Raises:
        HTTPException: If dates are invalid
    """
    try:
        start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid start_date format: {start_date}. Use ISO 8601 format.",
            )
    
    try:
        end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid end_date format: {end_date}. Use ISO 8601 format.",
            )
    
    if start_dt > end_dt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date must be before or equal to end_date",
        )
    
    return start_dt, end_dt


@router.get("/by-product", response_model=List[WasteByProductResponse])
def get_waste_by_product(
    start_date: str = Query(..., description="Start date in ISO 8601 format"),
    end_date: str = Query(..., description="End date in ISO 8601 format"),
    authorization: str = Query(None, alias="Authorization"),
    db: Session = Depends(get_db),
) -> WasteByProductResponse:
    """Get waste metrics grouped by product for a date range.
    
    Returns aggregated waste metrics per product for the given date range,
    including total quantity and cost wasted.
    
    Args:
        start_date: Start of date range (ISO 8601)
        end_date: End of date range (ISO 8601)
        authorization: Bearer token for authentication
        
    Returns:
        WasteByProductResponse with waste metrics grouped by product
        
    Raises:
        HTTPException: For invalid dates or authentication
    """
    # Validate authentication
    user_id = get_current_user_id_from_token(authorization)
    
    # Validate date range
    start_dt, end_dt = validate_date_range(start_date, end_date)
    
    logger.info(
        f"Getting waste by product for date range: {start_dt} to {end_dt}"
    )
    
    # Query waste metrics grouped by product
    waste_query = (
        db.query(
            WasteMetric.product_id,
            Product.name.label("product_name"),
            Product.category,
            func.sum(WasteMetric.total_quantity_wasted).label("total_quantity_wasted"),
            func.sum(WasteMetric.total_cost_wasted).label("total_cost_wasted"),
            func.count(WasteMetric.id).label("record_count"),
        )
        .join(Product, WasteMetric.product_id == Product.id)
        .filter(
            and_(
                WasteMetric.date >= start_dt,
                WasteMetric.date <= end_dt,
            )
        )
        .group_by(
            WasteMetric.product_id,
            Product.name,
            Product.category,
        )
        .order_by(func.sum(WasteMetric.total_cost_wasted).desc())
        .all()
    )
    
    # Build response
    waste_by_product = []
    for row in waste_query:
        waste_by_product.append(
            WasteByProductResponse(
                date=start_dt,
                product_id=row.product_id,
                product_name=row.product_name,
                waste_quantity=float(row.total_quantity_wasted or 0),
                waste_cost=float(row.total_cost_wasted or 0),
            )
        )
    
    total_quantity = sum(m.waste_quantity for m in waste_by_product)
    total_cost = sum(m.waste_cost for m in waste_by_product)
    
    logger.info(
        f"Found {len(waste_by_product)} products with waste. "
        f"Total quantity: {total_quantity}, Total cost: {total_cost}"
    )
    
    return waste_by_product


@router.get("/trend", response_model=List[WasteTrendResponse])
def get_waste_trend(
    product_id: int = Query(..., description="Product ID"),
    start_date: str = Query(..., description="Start date in ISO 8601 format"),
    end_date: str = Query(..., description="End date in ISO 8601 format"),
    authorization: str = Query(None, alias="Authorization"),
    db: Session = Depends(get_db),
) -> WasteTrendResponse:
    """Get time series of waste for a specific product.
    
    Returns daily waste metrics for a product over the given date range,
    useful for trend analysis and pattern detection.
    
    Args:
        product_id: ID of the product to query
        start_date: Start of date range (ISO 8601)
        end_date: End of date range (ISO 8601)
        authorization: Bearer token for authentication
        
    Returns:
        WasteTrendResponse with daily waste time series
        
    Raises:
        HTTPException: For invalid dates, product, or authentication
    """
    # Validate authentication
    user_id = get_current_user_id_from_token(authorization)
    
    # Validate product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found",
        )
    
    # Validate date range
    start_dt, end_dt = validate_date_range(start_date, end_date)
    
    logger.info(
        f"Getting waste trend for product {product_id} "
        f"({product.name}) from {start_dt} to {end_dt}"
    )
    
    # Query waste metrics for product over date range
    waste_metrics = (
        db.query(
            WasteMetric.date,
            WasteMetric.product_id,
            Product.name.label("product_name"),
            WasteMetric.total_quantity_wasted,
            WasteMetric.total_cost_wasted,
            WasteMetric.record_count,
        )
        .join(Product, WasteMetric.product_id == Product.id)
        .filter(
            and_(
                WasteMetric.product_id == product_id,
                WasteMetric.date >= start_dt,
                WasteMetric.date <= end_dt,
            )
        )
        .order_by(WasteMetric.date.asc())
        .all()
    )
    
    # Build time series response
    waste_trend = []
    for row in waste_metrics:
        waste_trend.append(
            WasteTrendResponse(
                date=row.date,
                product_id=row.product_id,
                product_name=row.product_name,
                waste_quantity=float(row.total_quantity_wasted or 0),
                waste_cost=float(row.total_cost_wasted or 0),
            )
        )
    
    total_quantity = sum(m.waste_quantity for m in waste_trend)
    total_cost = sum(m.waste_cost for m in waste_trend)
    
    logger.info(
        f"Found {len(waste_trend)} data points for product {product_id}. "
        f"Total quantity: {total_quantity}, Total cost: {total_cost}"
    )
    
    return waste_trend


@router.get("/summary", response_model=WasteSummaryResponse)
def get_waste_summary(
    start_date: str = Query(None, description="Start date in ISO 8601 format"),
    end_date: str = Query(None, description="End date in ISO 8601 format"),
    store_id: int = Query(None, description="Filter by store ID"),
    authorization: str = Query(None, alias="Authorization"),
    db: Session = Depends(get_db),
) -> WasteSummaryResponse:
    """Get overall waste summary statistics.
    
    Returns aggregated waste summary across all products and stores,
    with optional filtering by date range and store.
    
    Args:
        start_date: Start of date range (ISO 8601), defaults to 30 days ago
        end_date: End of date range (ISO 8601), defaults to today
        store_id: Optional store ID filter
        authorization: Bearer token for authentication
        
    Returns:
        WasteSummaryResponse with aggregated statistics
        
    Raises:
        HTTPException: For invalid dates, store, or authentication
    """
    # Validate authentication
    user_id = get_current_user_id_from_token(authorization)
    
    # Set default date range if not provided
    if not start_date or not end_date:
        end_dt = datetime.utcnow()
        start_dt = end_dt - timedelta(days=30)
        start_date = start_date or start_dt.isoformat()
        end_date = end_date or end_dt.isoformat()
    else:
        start_dt, end_dt = validate_date_range(start_date, end_date)
    
    # Validate store if provided
    if store_id:
        store = db.query(Store).filter(Store.id == store_id).first()
        if store is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Store with ID {store_id} not found",
            )
    
    logger.info(
        f"Getting waste summary for date range: {start_date} to {end_date}"
        f"{f' (store_id: {store_id})' if store_id else ''}"
    )
    
    # Build query filters
    filters = [
        WasteMetric.date >= start_dt,
        WasteMetric.date <= end_dt,
    ]
    if store_id:
        filters.append(WasteMetric.store_id == store_id)
    
    # Query aggregated statistics
    summary_query = (
        db.query(
            func.count(func.distinct(WasteMetric.product_id)).label("unique_products"),
            func.count(func.distinct(WasteMetric.store_id)).label("unique_stores"),
            func.sum(WasteMetric.total_quantity_wasted).label("total_quantity"),
            func.sum(WasteMetric.total_cost_wasted).label("total_cost"),
            func.sum(WasteMetric.record_count).label("total_records"),
            func.avg(WasteMetric.total_quantity_wasted).label("avg_daily_quantity"),
            func.avg(WasteMetric.total_cost_wasted).label("avg_daily_cost"),
        )
        .filter(and_(*filters))
        .first()
    )
    
    total_quantity = float(summary_query.total_quantity or 0)
    total_cost = float(summary_query.total_cost or 0)
    
    logger.info(
        f"Waste summary: {summary_query.unique_products} products, "
        f"{summary_query.unique_stores} stores, total waste: {total_cost}"
    )
    
    return WasteSummaryResponse(
        total_waste_quantity=total_quantity,
        total_waste_cost=total_cost,
        unique_products=summary_query.unique_products or 0,
        unique_stores=summary_query.unique_stores or 0,
        total_records=summary_query.total_records or 0,
        avg_daily_quantity=float(summary_query.avg_daily_quantity or 0),
        avg_daily_cost=float(summary_query.avg_daily_cost or 0),
        start_date=start_date,
        end_date=end_date,
    )


@router.post("/records", response_model=WasteRecordResponse, status_code=status.HTTP_201_CREATED)
def create_waste_record(
    record: CreateWasteRecordRequest,
    authorization: str = Query(None, alias="Authorization"),
    db: Session = Depends(get_db),
) -> WasteRecordResponse:
    """Create a new waste record.
    
    Records a new waste event with quantity, cost, and reason.
    
    Args:
        record: Waste record data
        authorization: Bearer token for authentication
        
    Returns:
        WasteRecordResponse with created record details
        
    Raises:
        HTTPException: For invalid data or authentication
    """
    # Validate authentication
    user_id = get_current_user_id_from_token(authorization)
    
    # Validate product exists
    product = db.query(Product).filter(Product.id == record.product_id).first()
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {record.product_id} not found",
        )
    
    # Validate store exists
    store = db.query(Store).filter(Store.id == record.store_id).first()
    if store is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Store with ID {record.store_id} not found",
        )
    
    # Create new waste record
    waste_record = WasteRecord(
        product_id=record.product_id,
        store_id=record.store_id,
        quantity_wasted=record.quantity_wasted,
        cost_wasted=record.cost_wasted,
        waste_reason=record.waste_reason,
        notes=record.notes,
        recorded_at=record.recorded_at or datetime.utcnow(),
    )
    
    db.add(waste_record)
    db.commit()
    db.refresh(waste_record)
    
    logger.info(
        f"Created waste record {waste_record.id} for product {record.product_id} "
        f"at store {record.store_id}, quantity: {record.quantity_wasted}"
    )
    
    return WasteRecordResponse(
        id=waste_record.id,
        product_id=waste_record.product_id,
        store_id=waste_record.store_id,
        quantity_wasted=waste_record.quantity_wasted,
        cost_wasted=waste_record.cost_wasted,
        waste_reason=waste_record.waste_reason,
        recorded_at=waste_record.recorded_at.isoformat(),
    )


@router.put("/records/{record_id}", response_model=WasteRecordResponse)
def update_waste_record(
    record_id: int,
    record_update: UpdateWasteRecordRequest,
    authorization: str = Query(None, alias="Authorization"),
    db: Session = Depends(get_db),
) -> WasteRecordResponse:
    """Update an existing waste record.
    
    Updates fields of an existing waste record.
    
    Args:
        record_id: ID of the waste record to update
        record_update: Updated record data
        authorization: Bearer token for authentication
        
    Returns:
        WasteRecordResponse with updated record details
        
    Raises:
        HTTPException: For invalid data, record not found, or authentication
    """
    # Validate authentication
    user_id = get_current_user_id_from_token(authorization)
    
    # Get existing record
    waste_record = db.query(WasteRecord).filter(WasteRecord.id == record_id).first()
    if waste_record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Waste record with ID {record_id} not found",
        )
    
    # Update fields if provided
    if record_update.quantity_wasted is not None:
        waste_record.quantity_wasted = record_update.quantity_wasted
    if record_update.cost_wasted is not None:
        waste_record.cost_wasted = record_update.cost_wasted
    if record_update.waste_reason is not None:
        waste_record.waste_reason = record_update.waste_reason
    if record_update.notes is not None:
        waste_record.notes = record_update.notes
    
    db.commit()
    db.refresh(waste_record)
    
    logger.info(f"Updated waste record {record_id}")
    
    return WasteRecordResponse(
        id=waste_record.id,
        product_id=waste_record.product_id,
        store_id=waste_record.store_id,
        quantity_wasted=waste_record.quantity_wasted,
        cost_wasted=waste_record.cost_wasted,
        waste_reason=waste_record.waste_reason,
        recorded_at=waste_record.recorded_at.isoformat(),
    )


@router.get("/records/{record_id}", response_model=WasteRecordResponse)
def get_waste_record(
    record_id: int,
    authorization: str = Query(None, alias="Authorization"),
    db: Session = Depends(get_db),
) -> WasteRecordResponse:
    """Get a specific waste record by ID.
    
    Args:
        record_id: ID of the waste record
        authorization: Bearer token for authentication
        
    Returns:
        WasteRecordResponse with record details
        
    Raises:
        HTTPException: For record not found or authentication
    """
    # Validate authentication
    user_id = get_current_user_id_from_token(authorization)
    
    # Get record
    waste_record = db.query(WasteRecord).filter(WasteRecord.id == record_id).first()
    if waste_record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Waste record with ID {record_id} not found",
        )
    
    return WasteRecordResponse(
        id=waste_record.id,
        product_id=waste_record.product_id,
        store_id=waste_record.store_id,
        quantity_wasted=waste_record.quantity_wasted,
        cost_wasted=waste_record.cost_wasted,
        waste_reason=waste_record.waste_reason,
        recorded_at=waste_record.recorded_at.isoformat(),
    )

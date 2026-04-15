"""
Waste Service Module

Business logic layer for waste management operations.
Provides functions for querying waste records, calculating metrics,
and managing waste data.
"""

import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.models.waste import WasteRecord, WasteMetric, Product, Store
from app.schemas.waste import (
    WasteByProductResponse,
    WasteTrendResponse,
    WasteSummaryResponse,
    CreateWasteRecordRequest,
    UpdateWasteRecordRequest,
    WasteRecordResponse,
)
from shared.utils import parse_date, format_datetime
from shared.constants import DEFAULT_WASTE_THRESHOLD

logger = logging.getLogger(__name__)


def get_waste_by_product(
    db: Session,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    store_id: Optional[int] = None,
) -> List[WasteByProductResponse]:
    """Get waste metrics grouped by product for a given date range.
    
    Args:
        db: Database session
        start_date: Start date for filtering (ISO 8601 string)
        end_date: End date for filtering (ISO 8601 string)
        store_id: Optional store ID to filter by
    
    Returns:
        List of waste metrics grouped by product
    """
    # Parse dates with defaults
    start_dt = parse_date(start_date) if start_date else datetime.utcnow()
    end_dt = parse_date(end_date) if end_date else datetime.utcnow()
    
    # Build query filters
    filters = [
        WasteMetric.date >= start_dt,
        WasteMetric.date <= end_dt,
    ]
    
    if store_id is not None:
        filters.append(WasteMetric.store_id == store_id)
    
    # Query aggregated waste by product
    results = (
        db.query(
            Product.id.label('product_id'),
            Product.name.label('product_name'),
            func.sum(WasteMetric.total_quantity_wasted).label('waste_quantity'),
            func.sum(WasteMetric.total_cost_wasted).label('waste_cost'),
            func.count(WasteMetric.id).label('record_count'),
        )
        .join(WasteMetric, WasteMetric.product_id == Product.id)
        .filter(and_(*filters))
        .group_by(Product.id, Product.name)
        .all()
    )
    
    return [
        WasteByProductResponse(
            product_id=r.product_id,
            product_name=r.product_name,
            waste_quantity=float(r.waste_quantity or 0),
            waste_cost=float(r.waste_cost or 0),
            record_count=r.record_count,
            start_date=start_date or format_datetime(start_dt),
            end_date=end_date or format_datetime(end_dt),
        )
        for r in results
    ]


def get_waste_trend(
    db: Session,
    product_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[WasteTrendResponse]:
    """Get time series of waste for a specific product.
    
    Args:
        db: Database session
        product_id: Product ID to get trends for
        start_date: Start date for filtering (ISO 8601 string)
        end_date: End date for filtering (ISO 8601 string)
    
    Returns:
        List of waste metrics over time for the product
    """
    # Parse dates with defaults
    start_dt = parse_date(start_date) if start_date else datetime.utcnow()
    end_dt = parse_date(end_date) if end_date else datetime.utcnow()
    
    # Query waste metrics for the product
    results = (
        db.query(
            WasteMetric.date,
            WasteMetric.product_id,
            Product.name.label('product_name'),
            WasteMetric.total_quantity_wasted.label('waste_quantity'),
            WasteMetric.total_cost_wasted.label('waste_cost'),
            WasteMetric.store_id,
            Store.name.label('store_name'),
        )
        .join(Product, WasteMetric.product_id == Product.id)
        .join(Store, WasteMetric.store_id == Store.id)
        .filter(
            and_(
                WasteMetric.product_id == product_id,
                WasteMetric.date >= start_dt,
                WasteMetric.date <= end_dt,
            )
        )
        .order_by(WasteMetric.date)
        .all()
    )
    
    return [
        WasteTrendResponse(
            date=format_datetime(r.date),
            product_id=r.product_id,
            product_name=r.product_name,
            waste_quantity=float(r.waste_quantity or 0),
            waste_cost=float(r.waste_cost or 0),
            store_id=r.store_id,
            store_name=r.store_name,
        )
        for r in results
    ]


def get_waste_summary(
    db: Session,
    product_id: Optional[int] = None,
    store_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> WasteSummaryResponse:
    """Get aggregated waste summary for dashboard.
    
    Args:
        db: Database session
        product_id: Optional product ID to filter by
        store_id: Optional store ID to filter by
        start_date: Start date for filtering (ISO 8601 string)
        end_date: End date for filtering (ISO 8601 string)
    
    Returns:
        Aggregated waste summary
    """
    # Parse dates with defaults
    start_dt = parse_date(start_date) if start_date else datetime.utcnow()
    end_dt = parse_date(end_date) if end_date else datetime.utcnow()
    
    # Build filters
    filters = [
        WasteMetric.date >= start_dt,
        WasteMetric.date <= end_dt,
    ]
    
    if product_id is not None:
        filters.append(WasteMetric.product_id == product_id)
    
    if store_id is not None:
        filters.append(WasteMetric.store_id == store_id)
    
    # Get aggregated totals
    result = (
        db.query(
            func.sum(WasteMetric.total_quantity_wasted).label('total_quantity'),
            func.sum(WasteMetric.total_cost_wasted).label('total_cost'),
            func.count(WasteMetric.id).label('record_count'),
        )
        .filter(and_(*filters))
        .first()
    )
    
    total_quantity = float(result.total_quantity or 0)
    total_cost = float(result.total_cost or 0)
    
    return WasteSummaryResponse(
        total_waste_quantity=total_quantity,
        total_waste_cost=total_cost,
        record_count=result.record_count or 0,
        start_date=start_date or format_datetime(start_dt),
        end_date=end_date or format_datetime(end_dt),
    )


def create_waste_record(
    db: Session,
    data: CreateWasteRecordRequest,
) -> WasteRecordResponse:
    """Create a new waste record.
    
    Args:
        db: Database session
        data: Waste record creation data
    
    Returns:
        Created waste record
    """
    # Verify product exists
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise ValueError(f"Product with ID {data.product_id} not found")
    
    # Verify store exists
    store = db.query(Store).filter(Store.id == data.store_id).first()
    if not store:
        raise ValueError(f"Store with ID {data.store_id} not found")
    
    # Create waste record
    waste_record = WasteRecord(
        product_id=data.product_id,
        store_id=data.store_id,
        quantity_wasted=data.quantity_wasted,
        cost_wasted=data.cost_wasted,
        waste_reason=data.waste_reason,
        notes=data.notes,
        recorded_at=parse_date(data.recorded_at) if data.recorded_at else datetime.utcnow(),
    )
    
    db.add(waste_record)
    db.commit()
    db.refresh(waste_record)
    
    # Update or create daily metric
    _update_daily_waste_metric(db, waste_record)
    
    return WasteRecordResponse(
        id=waste_record.id,
        product_id=waste_record.product_id,
        product_name=product.name,
        store_id=waste_record.store_id,
        store_name=store.name,
        quantity_wasted=waste_record.quantity_wasted,
        cost_wasted=waste_record.cost_wasted,
        waste_reason=waste_record.waste_reason,
        notes=waste_record.notes,
        recorded_at=format_datetime(waste_record.recorded_at),
        created_at=format_datetime(waste_record.created_at),
    )


def update_waste_record(
    db: Session,
    record_id: int,
    data: UpdateWasteRecordRequest,
) -> WasteRecordResponse:
    """Update an existing waste record.
    
    Args:
        db: Database session
        record_id: ID of the record to update
        data: Update data
    
    Returns:
        Updated waste record
    """
    waste_record = db.query(WasteRecord).filter(WasteRecord.id == record_id).first()
    
    if not waste_record:
        raise ValueError(f"Waste record with ID {record_id} not found")
    
    # Update fields if provided
    if data.quantity_wasted is not None:
        waste_record.quantity_wasted = data.quantity_wasted
    
    if data.cost_wasted is not None:
        waste_record.cost_wasted = data.cost_wasted
    
    if data.waste_reason is not None:
        waste_record.waste_reason = data.waste_reason
    
    if data.notes is not None:
        waste_record.notes = data.notes
    
    db.commit()
    db.refresh(waste_record)
    
    # Get related objects for response
    product = db.query(Product).filter(Product.id == waste_record.product_id).first()
    store = db.query(Store).filter(Store.id == waste_record.store_id).first()
    
    return WasteRecordResponse(
        id=waste_record.id,
        product_id=waste_record.product_id,
        product_name=product.name if product else "Unknown",
        store_id=waste_record.store_id,
        store_name=store.name if store else "Unknown",
        quantity_wasted=waste_record.quantity_wasted,
        cost_wasted=waste_record.cost_wasted,
        waste_reason=waste_record.waste_reason,
        notes=waste_record.notes,
        recorded_at=format_datetime(waste_record.recorded_at),
        created_at=format_datetime(waste_record.created_at),
    )


def delete_waste_record(db: Session, record_id: int) -> bool:
    """Delete a waste record.
    
    Args:
        db: Database session
        record_id: ID of the record to delete
    
    Returns:
        True if deleted successfully
    """
    waste_record = db.query(WasteRecord).filter(WasteRecord.id == record_id).first()
    
    if not waste_record:
        raise ValueError(f"Waste record with ID {record_id} not found")
    
    db.delete(waste_record)
    db.commit()
    
    return True


def _update_daily_waste_metric(db: Session, waste_record: WasteRecord) -> None:
    """Update or create daily waste metric for a waste record.
    
    Args:
        db: Database session
        waste_record: The waste record to aggregate
    """
    # Get the date portion of recorded_at
    record_date = waste_record.recorded_at.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Check if metric exists for this product/store/date
    metric = (
        db.query(WasteMetric)
        .filter(
            and_(
                WasteMetric.product_id == waste_record.product_id,
                WasteMetric.store_id == waste_record.store_id,
                WasteMetric.date == record_date,
            )
        )
        .first()
    )
    
    if metric:
        # Update existing metric
        metric.total_quantity_wasted += waste_record.quantity_wasted
        metric.total_cost_wasted += waste_record.cost_wasted
        metric.record_count += 1
    else:
        # Create new metric
        metric = WasteMetric(
            product_id=waste_record.product_id,
            store_id=waste_record.store_id,
            date=record_date,
            total_quantity_wasted=waste_record.quantity_wasted,
            total_cost_wasted=waste_record.cost_wasted,
            record_count=1,
        )
        db.add(metric)
    
    db.commit()


def get_products_with_waste(
    db: Session,
    limit: int = 100,
    offset: int = 0,
) -> List[dict]:
    """Get list of products that have waste records.
    
    Args:
        db: Database session
        limit: Maximum number of results
        offset: Number of results to skip
    
    Returns:
        List of products with waste data
    """
    results = (
        db.query(
            Product.id,
            Product.sku,
            Product.name,
            Product.category,
            func.sum(WasteMetric.total_quantity_wasted).label('total_waste'),
            func.sum(WasteMetric.total_cost_wasted).label('total_cost'),
        )
        .join(WasteMetric, WasteMetric.product_id == Product.id)
        .group_by(Product.id, Product.sku, Product.name, Product.category)
        .order_by(func.sum(WasteMetric.total_cost_wasted).desc())
        .limit(limit)
        .offset(offset)
        .all()
    )
    
    return [
        {
            "id": r.id,
            "sku": r.sku,
            "name": r.name,
            "category": r.category,
            "total_waste": float(r.total_waste or 0),
            "total_cost": float(r.total_cost or 0),
        }
        for r in results
    ]


def calculate_waste_percentage(
    db: Session,
    product_id: int,
    store_id: Optional[int] = None,
    days: int = 30,
) -> float:
    """Calculate waste percentage for a product over a period.
    
    Args:
        db: Database session
        product_id: Product ID
        store_id: Optional store ID
        days: Number of days to look back
    
    Returns:
        Waste percentage (0-100)
    """
    from datetime import timedelta
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    filters = [
        WasteMetric.product_id == product_id,
        WasteMetric.date >= start_date,
        WasteMetric.date <= end_date,
    ]
    
    if store_id is not None:
        filters.append(WasteMetric.store_id == store_id)
    
    # Get total waste quantity
    result = (
        db.query(
            func.sum(WasteMetric.total_quantity_wasted).label('total_waste')
        )
        .filter(and_(*filters))
        .first()
    )
    
    total_waste = float(result.total_waste or 0)
    
    # For a proper percentage, we'd need inventory data
    # This is a simplified version
    # In production, this would calculate: waste / (waste + sold) * 100
    
    return total_waste


def get_top_waste_products(
    db: Session,
    limit: int = 10,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[dict]:
    """Get products with the highest waste costs.
    
    Args:
        db: Database session
        limit: Number of top products to return
        start_date: Start date for filtering
        end_date: End date for filtering
    
    Returns:
        List of top waste products
    """
    start_dt = parse_date(start_date) if start_date else datetime.utcnow()
    end_dt = parse_date(end_date) if end_date else datetime.utcnow()
    
    results = (
        db.query(
            Product.id,
            Product.sku,
            Product.name,
            Product.category,
            func.sum(WasteMetric.total_quantity_wasted).label('total_quantity'),
            func.sum(WasteMetric.total_cost_wasted).label('total_cost'),
        )
        .join(WasteMetric, WasteMetric.product_id == Product.id)
        .filter(
            and_(
                WasteMetric.date >= start_dt,
                WasteMetric.date <= end_dt,
            )
        )
        .group_by(Product.id, Product.sku, Product.name, Product.category)
        .order_by(func.sum(WasteMetric.total_cost_wasted).desc())
        .limit(limit)
        .all()
    )
    
    return [
        {
            "product_id": r.id,
            "sku": r.sku,
            "name": r.name,
            "category": r.category,
            "total_quantity": float(r.total_quantity or 0),
            "total_cost": float(r.total_cost or 0),
        }
        for r in results
    ]


def get_waste_by_store(
    db: Session,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[dict]:
    """Get waste metrics aggregated by store.
    
    Args:
        db: Database session
        start_date: Start date for filtering
        end_date: End date for filtering
    
    Returns:
        List of waste metrics by store
    """
    start_dt = parse_date(start_date) if start_date else datetime.utcnow()
    end_dt = parse_date(end_date) if end_date else datetime.utcnow()
    
    results = (
        db.query(
            Store.id,
            Store.store_code,
            Store.name,
            Store.region,
            func.sum(WasteMetric.total_quantity_wasted).label('total_quantity'),
            func.sum(WasteMetric.total_cost_wasted).label('total_cost'),
            func.count(WasteMetric.id).label('record_count'),
        )
        .join(WasteMetric, WasteMetric.store_id == Store.id)
        .filter(
            and_(
                WasteMetric.date >= start_dt,
                WasteMetric.date <= end_dt,
            )
        )
        .group_by(Store.id, Store.store_code, Store.name, Store.region)
        .order_by(func.sum(WasteMetric.total_cost_wasted).desc())
        .all()
    )
    
    return [
        {
            "store_id": r.id,
            "store_code": r.store_code,
            "store_name": r.name,
            "region": r.region,
            "total_quantity": float(r.total_quantity or 0),
            "total_cost": float(r.total_cost or 0),
            "record_count": r.record_count,
        }
        for r in results
    ]

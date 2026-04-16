"""
Dashboard API Endpoints

REST API endpoints for dashboard metrics, including waste tracking,
alerts, and demand predictions.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Header, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import decode_access_token, verify_token_and_get_user_id
from app.db.session import get_db
from app.models.alert import Alert
from app.models.waste import Product, WasteMetric
from app.models.demand import DemandPrediction
from app.schemas.dashboard import (
    DashboardMetricsResponse,
    WasteMetric as WasteMetricSchema,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def get_current_user_id_from_token(
    authorization: Optional[str] = None
) -> Optional[int]:
    """
    Extract and validate user ID from Authorization header.
    
    Args:
        authorization: Authorization header value
        
    Returns:
        User ID if token is valid, None otherwise
        
    Raises:
        HTTPException: 401 if token is invalid
    """
    # This is a placeholder that will be replaced by the actual dependency
    pass


async def get_current_user(
    authorization: Optional[str] = Header(None)
) -> int:
    """
    Dependency to get current authenticated user from JWT token.
    
    Args:
        authorization: Authorization header with Bearer token
        
    Returns:
        User ID from the token
        
    Raises:
        HTTPException: 401 if token is missing or invalid
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract token from "Bearer <token>" format
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Use 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = parts[1]
    
    # Verify token and get user ID
    user_id = verify_token_and_get_user_id(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id


@router.get("/metrics", response_model=DashboardMetricsResponse)
async def get_dashboard_metrics(
    current_user: int = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = Query(default=30, ge=1, le=365, description="Number of days to look back"),
    store_id: Optional[int] = Query(default=None, description="Filter by store ID"),
) -> DashboardMetricsResponse:
    """
    Get consolidated dashboard metrics including waste totals, trends, alerts, and demand predictions.
    
    Args:
        current_user: Authenticated user ID from JWT token
        db: Database session
        days: Number of days to look back for metrics (default: 30)
        store_id: Optional store filter
        
    Returns:
        DashboardMetricsResponse with waste metrics, trends, alerts, and demand prediction
    """
    try:
        # Calculate date range
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        
        # Build base query filters
        metric_filters = [WasteMetric.date >= start_date, WasteMetric.date <= end_date]
        alert_filters = [Alert.created_at >= start_date, Alert.is_active == 1]
        
        if store_id is not None:
            metric_filters.append(WasteMetric.store_id == store_id)
            alert_filters.append(Alert.store_id == store_id)
        
        # Get total waste quantity and cost
        total_waste_query = db.query(
            func.coalesce(func.sum(WasteMetric.total_quantity_wasted), 0.0),
            func.coalesce(func.sum(WasteMetric.total_cost_wasted), 0.0),
        ).filter(*metric_filters)
        
        total_result = total_waste_query.first()
        total_waste_quantity = float(total_result[0]) if total_result[0] is not None else 0.0
        total_waste_cost = float(total_result[1]) if total_result[1] is not None else 0.0
        
        # Get waste by product (aggregated)
        waste_by_product_query = (
            db.query(
                WasteMetric.product_id,
                Product.name,
                func.sum(WasteMetric.total_quantity_wasted).label("total_quantity"),
                func.sum(WasteMetric.total_cost_wasted).label("total_cost"),
                func.max(WasteMetric.date).label("latest_date"),
            )
            .join(Product, WasteMetric.product_id == Product.id)
            .filter(*metric_filters)
            .group_by(WasteMetric.product_id, Product.name)
            .order_by(func.sum(WasteMetric.total_cost_wasted).desc())
            .limit(20)
        )
        
        waste_by_product: List[WasteMetricSchema] = []
        for row in waste_by_product_query.all():
            waste_by_product.append(
                WasteMetricSchema(
                    date=row.latest_date.isoformat() if row.latest_date else start_date.isoformat(),
                    product_id=row.product_id,
                    product_name=row.name,
                    waste_quantity=float(row.total_quantity) if row.total_quantity else 0.0,
                    waste_cost=float(row.total_cost) if row.total_cost else 0.0,
                )
            )
        
        # Get waste trend (time series - daily aggregates for last 30 days)
        waste_trend_query = (
            db.query(
                func.date(WasteMetric.date).label("date_only"),
                func.sum(WasteMetric.total_quantity_wasted).label("total_quantity"),
                func.sum(WasteMetric.total_cost_wasted).label("total_cost"),
            )
            .filter(*metric_filters)
            .group_by(func.date(WasteMetric.date))
            .order_by(func.date(WasteMetric.date))
        )
        
        waste_trend: List[WasteMetricSchema] = []
        # Group by product for trend - get top 5 products
        top_products = (
            db.query(WasteMetric.product_id)
            .filter(*metric_filters)
            .group_by(WasteMetric.product_id)
            .order_by(func.sum(WasteMetric.total_cost_wasted).desc())
            .limit(5)
            .all()
        )
        
        top_product_ids = [p[0] for p in top_products]
        
        if top_product_ids:
            trend_filters = metric_filters + [WasteMetric.product_id.in_(top_product_ids)]
            waste_trend_query = (
                db.query(
                    WasteMetric.date,
                    WasteMetric.product_id,
                    Product.name,
                    func.sum(WasteMetric.total_quantity_wasted).label("total_quantity"),
                    func.sum(WasteMetric.total_cost_wasted).label("total_cost"),
                )
                .join(Product, WasteMetric.product_id == Product.id)
                .filter(*trend_filters)
                .group_by(
                    WasteMetric.date,
                    WasteMetric.product_id,
                    Product.name,
                )
                .order_by(WasteMetric.date)
            )
            
            for row in waste_trend_query.all():
                waste_trend.append(
                    WasteMetricSchema(
                        date=row.date.isoformat(),
                        product_id=row.product_id,
                        product_name=row.name,
                        waste_quantity=float(row.total_quantity) if row.total_quantity else 0.0,
                        waste_cost=float(row.total_cost) if row.total_cost else 0.0,
                    )
                )
        
        # Get active alerts
        alerts_query = (
            db.query(Alert.message)
            .filter(*alert_filters)
            .order_by(Alert.created_at.desc())
            .limit(50)
        )
        
        alerts: List[str] = [row[0] for row in alerts_query.all()]
        
        # Get demand prediction (latest prediction for any product)
        demand_prediction: Optional[float] = None
        prediction_query = (
            db.query(DemandPrediction.predicted_demand)
            .filter(
                DemandPrediction.prediction_date >= start_date,
                DemandPrediction.prediction_date <= end_date,
            )
            .order_by(DemandPrediction.created_at.desc())
            .limit(1)
        )
        
        pred_result = prediction_query.first()
        if pred_result and pred_result[0] is not None:
            demand_prediction = float(pred_result[0])
        
        # Build response
        response = DashboardMetricsResponse(
            total_waste_quantity=total_waste_quantity,
            total_waste_cost=total_waste_cost,
            waste_by_product=waste_by_product,
            waste_trend=waste_trend,
            alerts=alerts,
        )
        
        # Only include demand_prediction if it exists
        if demand_prediction is not None:
            response.demand_prediction = demand_prediction
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching dashboard metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch dashboard metrics",
        )

"""
Dashboard Service

Provides business logic for dashboard metrics aggregation.
Handles data retrieval from waste records, alerts, and demand predictions
to compile comprehensive dashboard metrics.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple

from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session

from app.models.waste import WasteRecord, WasteMetric, Product
from app.models.alert import Alert
from app.models.demand import DemandPrediction
from app.schemas.dashboard import (
    DashboardMetricsResponse,
    WasteMetric as WasteMetricSchema,
)
from shared.constants import (
    AlertSeverity,
    ISO8601_FORMAT,
    DEFAULT_WASTE_THRESHOLD,
    CRITICAL_WASTE_THRESHOLD,
)
from shared.utils import to_iso8601, format_datetime

logger = logging.getLogger(__name__)


class DashboardService:
    """Service for aggregating dashboard metrics.
    
    Provides methods to retrieve and aggregate waste metrics,
    alerts, and demand predictions for the dashboard display.
    """
    
    def __init__(self, db: Session):
        """Initialize dashboard service with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def get_dashboard_metrics(
        self,
        store_id: Optional[int] = None,
        days_back: int = 30
    ) -> DashboardMetricsResponse:
        """Get comprehensive dashboard metrics.
        
        Retrieves aggregated waste metrics, trends, alerts, and
        demand predictions for the dashboard display.
        
        Args:
            store_id: Optional store ID to filter metrics
            days_back: Number of days to look back for metrics
            
        Returns:
            DashboardMetricsResponse with all aggregated metrics
        """
        try:
            # Calculate date range
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=days_back)
            
            # Build base filter conditions
            waste_filters = [
                WasteRecord.recorded_at >= start_date,
                WasteRecord.recorded_at <= end_date,
            ]
            if store_id:
                waste_filters.append(WasteRecord.store_id == store_id)
            
            # Get total waste quantities and costs
            waste_totals = self._get_waste_totals(waste_filters)
            total_waste_quantity = waste_totals.get('total_quantity', 0.0)
            total_waste_cost = waste_totals.get('total_cost', 0.0)
            
            # Get waste by product
            waste_by_product = self._get_waste_by_product(
                waste_filters,
                start_date,
                end_date
            )
            
            # Get waste trend (time series)
            waste_trend = self._get_waste_trend(
                waste_filters,
                start_date,
                end_date
            )
            
            # Get active alerts
            alerts = self._get_active_alerts(store_id)
            
            # Get demand prediction if available
            demand_prediction = self._get_latest_demand_prediction(store_id)
            
            # Build response
            return DashboardMetricsResponse(
                total_waste_quantity=total_waste_quantity,
                total_waste_cost=total_waste_cost,
                waste_by_product=waste_by_product,
                waste_trend=waste_trend,
                alerts=alerts,
                demand_prediction=demand_prediction
            )
            
        except Exception as e:
            logger.error(f"Error getting dashboard metrics: {e}")
            # Return empty response on error to maintain service availability
            return DashboardMetricsResponse(
                total_waste_quantity=0.0,
                total_waste_cost=0.0,
                waste_by_product=[],
                waste_trend=[],
                alerts=[],
                demand_prediction=None
            )
    
    def _get_waste_totals(self, filters: List) -> dict:
        """Get total waste quantity and cost.
        
        Args:
            filters: List of filter conditions for waste records
            
        Returns:
            Dictionary with total_quantity and total_cost
        """
        try:
            result = self.db.query(
                func.sum(WasteRecord.quantity_wasted).label('total_quantity'),
                func.sum(WasteRecord.cost_wasted).label('total_cost')
            ).filter(*filters).first()
            
            return {
                'total_quantity': float(result.total_quantity or 0.0),
                'total_cost': float(result.total_cost or 0.0)
            }
        except Exception as e:
            logger.error(f"Error getting waste totals: {e}")
            return {'total_quantity': 0.0, 'total_cost': 0.0}
    
    def _get_waste_by_product(
        self,
        filters: List,
        start_date: datetime,
        end_date: datetime
    ) -> List[WasteMetricSchema]:
        """Get waste metrics grouped by product.
        
        Args:
            filters: List of filter conditions
            start_date: Start date for aggregation
            end_date: End date for aggregation
            
        Returns:
            List of WasteMetricSchema for each product
        """
        try:
            # Join with products to get product names
            results = (
                self.db.query(
                    Product.id.label('product_id'),
                    Product.name.label('product_name'),
                    func.sum(WasteRecord.quantity_wasted).label('waste_quantity'),
                    func.sum(WasteRecord.cost_wasted).label('waste_cost'),
                    func.max(WasteRecord.recorded_at).label('date')
                )
                .join(Product, WasteRecord.product_id == Product.id)
                .filter(*filters)
                .group_by(Product.id, Product.name)
                .order_by(func.sum(WasteRecord.cost_wasted).desc())
                .limit(20)
                .all()
            )
            
            waste_metrics = []
            for row in results:
                waste_metrics.append(
                    WasteMetricSchema(
                        date=row.date,
                        product_id=row.product_id,
                        product_name=row.product_name,
                        waste_quantity=float(row.waste_quantity or 0.0),
                        waste_cost=float(row.waste_cost or 0.0)
                    )
                )
            
            return waste_metrics
            
        except Exception as e:
            logger.error(f"Error getting waste by product: {e}")
            return []
    
    def _get_waste_trend(
        self,
        filters: List,
        start_date: datetime,
        end_date: datetime
    ) -> List[WasteMetricSchema]:
        """Get time series of waste over date range.
        
        Args:
            filters: List of filter conditions
            start_date: Start date for trend
            end_date: End date for trend
            
        Returns:
            List of WasteMetricSchema ordered by date
        """
        try:
            results = (
                self.db.query(
                    func.date(WasteRecord.recorded_at).label('date'),
                    func.sum(WasteRecord.quantity_wasted).label('waste_quantity'),
                    func.sum(WasteRecord.cost_wasted).label('waste_cost')
                )
                .filter(*filters)
                .group_by(func.date(WasteRecord.recorded_at))
                .order_by(func.date(WasteRecord.recorded_at).desc())
                .limit(30)
                .all()
            )
            
            # Get all products for trend (aggregate)
            product_info = self.db.query(Product).first()
            default_product_id = product_info.id if product_info else 1
            default_product_name = product_info.name if product_info else "All Products"
            
            trend_metrics = []
            for row in results:
                # Convert date to datetime for schema
                date_val = row.date if isinstance(row.date, datetime) else datetime.combine(
                    row.date, datetime.min.time()
                )
                trend_metrics.append(
                    WasteMetricSchema(
                        date=date_val,
                        product_id=default_product_id,
                        product_name=default_product_name,
                        waste_quantity=float(row.waste_quantity or 0.0),
                        waste_cost=float(row.waste_cost or 0.0)
                    )
                )
            
            # Sort by date ascending for chart display
            trend_metrics.sort(key=lambda x: x.date)
            return trend_metrics
            
        except Exception as e:
            logger.error(f"Error getting waste trend: {e}")
            return []
    
    def _get_active_alerts(self, store_id: Optional[int] = None) -> List[str]:
        """Get active alert messages.
        
        Args:
            store_id: Optional store ID to filter alerts
            
        Returns:
            List of alert message strings
        """
        try:
            filters = [Alert.is_active == 1]
            if store_id:
                filters.append(Alert.store_id == store_id)
            
            results = (
                self.db.query(Alert.message)
                .filter(*filters)
                .order_by(Alert.created_at.desc())
                .limit(10)
                .all()
            )
            
            return [row.message for row in results]
            
        except Exception as e:
            logger.error(f"Error getting active alerts: {e}")
            return []
    
    def _get_latest_demand_prediction(
        self,
        store_id: Optional[int] = None
    ) -> Optional[float]:
        """Get the latest demand prediction value.
        
        Args:
            store_id: Optional store ID to filter predictions
            
        Returns:
            Latest predicted demand value or None
        """
        try:
                filters = [DemandPrediction.prediction_date >= datetime.now(timezone.utc)]
            if store_id:
                filters.append(DemandPrediction.store_id == store_id)
            
            result = (
                self.db.query(DemandPrediction.predicted_demand)
                .filter(*filters)
                .order_by(DemandPrediction.prediction_date.asc())
                .first()
            )
            
            if result:
                return float(result.predicted_demand)
            return None
            
        except Exception as e:
            logger.error(f"Error getting demand prediction: {e}")
            return None
    
    def get_dashboard_metrics_with_defaults(
        self,
        store_id: Optional[int] = None
    ) -> DashboardMetricsResponse:
        """Get dashboard metrics with default 30-day window.
        
        Convenience method that uses default 30-day lookback.
        
        Args:
            store_id: Optional store ID to filter metrics
            
        Returns:
            DashboardMetricsResponse with aggregated metrics
        """
        return self.get_dashboard_metrics(store_id=store_id, days_back=30)


def get_dashboard_service(db: Session) -> DashboardService:
    """Factory function to create DashboardService instance.
    
    Args:
        db: SQLAlchemy database session
        
    Returns:
        DashboardService instance
    """
    return DashboardService(db)

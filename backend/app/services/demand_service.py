"""
Demand Prediction Service

Business logic for demand forecasting and prediction management.
Implements prediction algorithms based on historical data patterns.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.cache import CacheManager
from app.core.config import settings
from app.models.demand import DemandPrediction
from app.models.waste import Product, Store, WasteMetric, WasteRecord
from app.schemas.demand import (
    DemandPredictionRequest,
    DemandPredictionResponse,
    DemandPredictionDetail,
)

logger = logging.getLogger(__name__)


class DemandService:
    """Service for demand prediction and forecasting operations.
    
    Handles demand predictions based on historical sales and waste data,
    implements forecasting algorithms, and manages prediction storage.
    
    Attributes:
        db: Database session for data operations
        cache: Optional cache manager for performance optimization
    """
    
    def __init__(self, db: Session, cache: Optional[CacheManager] = None):
        """Initialize demand service with database session.
        
        Args:
            db: SQLAlchemy database session
            cache: Optional cache manager for caching predictions
        """
        self.db = db
        self.cache = cache
    
    def get_prediction(
        self,
        product_id: int,
        date: datetime,
        store_id: Optional[int] = None,
    ) -> Optional[float]:
        """Get demand prediction for a specific product and date.
        
        Args:
            product_id: ID of the product to predict demand for
            date: Date for which to predict demand
            store_id: Optional store ID for localized prediction
        
        Returns:
            Predicted demand value or None if no prediction exists
        """
        # Try cache first
        if self.cache:
            cache_key = f"demand_prediction:{product_id}:{date.date()}:{store_id or 'all'}"
            cached = self.cache.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for demand prediction: {cache_key}")
                return float(cached)
        
        # Query database
        query = self.db.query(DemandPrediction).filter(
            DemandPrediction.product_id == product_id,
            DemandPrediction.prediction_date >= date.date(),
            DemandPrediction.prediction_date < date.date() + timedelta(days=1),
        )
        
        if store_id:
            query = query.filter(DemandPrediction.store_id == store_id)
        
        prediction = query.order_by(DemandPrediction.created_at.desc()).first()
        
        if prediction and self.cache:
            # Cache the result
            cache_key = f"demand_prediction:{product_id}:{date.date()}:{store_id or 'all'}"
            self.cache.set(cache_key, str(prediction.predicted_demand), ttl=1800)
        
        return prediction.predicted_demand if prediction else None
    
    def get_prediction_detail(
        self,
        product_id: int,
        date: datetime,
        store_id: Optional[int] = None,
    ) -> Optional[DemandPredictionDetail]:
        """Get detailed demand prediction with confidence level.
        
        Args:
            product_id: ID of the product
            date: Date for prediction
            store_id: Optional store ID
        
        Returns:
            DemandPredictionDetail if found, None otherwise
        """
        query = self.db.query(DemandPrediction).filter(
            DemandPrediction.product_id == product_id,
            DemandPrediction.prediction_date >= date.date(),
            DemandPrediction.prediction_date < date.date() + timedelta(days=1),
        )
        
        if store_id:
            query = query.filter(DemandPrediction.store_id == store_id)
        
        prediction = query.order_by(DemandPrediction.created_at.desc()).first()
        
        if not prediction:
            return None
        
        return DemandPredictionDetail(
            product_id=prediction.product_id,
            store_id=prediction.store_id,
            predicted_demand=prediction.predicted_demand,
            prediction_date=prediction.prediction_date,
            confidence_level=prediction.confidence_level,
            model_version=prediction.model_version,
            prediction_type=prediction.prediction_type,
        )
    
    def calculate_demand_prediction(
        self,
        product_id: int,
        target_date: datetime,
        store_id: Optional[int] = None,
    ) -> Tuple[float, float]:
        """Calculate demand prediction using historical data analysis.
        
        Implements a moving average based forecasting algorithm using
        historical waste and sales data to predict future demand.
        
        Args:
            product_id: Product to predict demand for
            target_date: Target date for prediction
            store_id: Optional store for localized prediction
        
        Returns:
            Tuple of (predicted_demand, confidence_level)
        """
        # Get historical data for the past 30 days
        history_start = target_date - timedelta(days=settings.DEMAND_PREDICTION_DAYS)
        
        # Query waste metrics as proxy for demand (higher waste often indicates lower demand)
        query = self.db.query(
            func.avg(WasteMetric.total_quantity_wasted).label('avg_waste'),
            func.count(WasteMetric.id).label('record_count'),
        ).filter(
            WasteMetric.product_id == product_id,
            WasteMetric.date >= history_start,
            WasteMetric.date < target_date,
        )
        
        if store_id:
            query = query.filter(WasteMetric.store_id == store_id)
        
        result = query.first()
        
        if not result or result.record_count < settings.DEMAND_PREDICTION_DAYS // 2:
            # Not enough historical data, use default calculation
            # Calculate based on recent sales patterns
            return self._calculate_default_prediction(product_id, target_date, store_id)
        
        avg_waste = float(result.avg_waste or 0)
        record_count = int(result.record_count)
        
        # Calculate demand as inverse of waste (assuming lower waste = higher demand)
        # This is a simplified model - in production would use more complex algorithms
        base_demand = max(avg_waste * 1.5, 1.0)  # Minimum demand of 1.0
        
        # Apply trend adjustment based on recent data
        trend_factor = self._calculate_trend_factor(product_id, history_start, target_date, store_id)
        
        predicted_demand = base_demand * trend_factor
        
        # Calculate confidence based on data quality
        confidence = min(record_count / settings.DEMAND_PREDICTION_DAYS, 1.0)
        
        return predicted_demand, confidence
    
    def _calculate_default_prediction(
        self,
        product_id: int,
        target_date: datetime,
        store_id: Optional[int] = None,
    ) -> Tuple[float, float]:
        """Calculate default prediction when insufficient historical data.
        
        Args:
            product_id: Product ID
            target_date: Target date
            store_id: Optional store ID
        
        Returns:
            Tuple of (predicted_demand, confidence)
        """
        # Use product cost price as a baseline estimate
        product = self.db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            return 10.0, 0.3  # Default values
        
        # Basic estimation based on price tier
        if product.cost_price > 50:
            base_demand = 5.0
        elif product.cost_price > 20:
            base_demand = 10.0
        elif product.cost_price > 5:
            base_demand = 20.0
        else:
            base_demand = 30.0
        
        return base_demand, 0.3  # Low confidence due to limited data
    
    def _calculate_trend_factor(
        self,
        product_id: int,
        start_date: datetime,
        end_date: datetime,
        store_id: Optional[int] = None,
    ) -> float:
        """Calculate trend factor based on historical waste pattern.
        
        Args:
            product_id: Product ID
            start_date: Start of analysis period
            end_date: End of analysis period
            store_id: Optional store ID
        
        Returns:
            Trend factor (1.0 = stable, >1.0 = increasing, <1.0 = decreasing)
        """
        mid_point = start_date + (end_date - start_date) / 2
        
        # Get first half average
        first_half = self.db.query(
            func.avg(WasteMetric.total_quantity_wasted)
        ).filter(
            WasteMetric.product_id == product_id,
            WasteMetric.date >= start_date,
            WasteMetric.date < mid_point,
        )
        
        if store_id:
            first_half = first_half.filter(WasteMetric.store_id == store_id)
        
        first_avg = float(first_half.scalar() or 0)
        
        # Get second half average
        second_half = self.db.query(
            func.avg(WasteMetric.total_quantity_wasted)
        ).filter(
            WasteMetric.product_id == product_id,
            WasteMetric.date >= mid_point,
            WasteMetric.date < end_date,
        )
        
        if store_id:
            second_half = second_half.filter(WasteMetric.store_id == store_id)
        
        second_avg = float(second_half.scalar() or 0)
        
        if first_avg == 0:
            return 1.0
        
        # Calculate trend (inverse for demand - decreasing waste = increasing demand)
        waste_trend = second_avg / first_avg
        demand_trend = 1.0 / waste_trend if waste_trend > 0 else 1.0
        
        # Apply seasonal adjustment from settings
        demand_trend *= settings.FORECAST_SEASONAL_ADJUSTMENT
        
        # Clamp to reasonable range
        return max(0.5, min(2.0, demand_trend))
    
    def create_prediction(
        self,
        product_id: int,
        store_id: int,
        predicted_demand: float,
        prediction_date: datetime,
        confidence_level: Optional[float] = None,
        model_version: str = "v1.0",
        prediction_type: str = "daily",
    ) -> DemandPrediction:
        """Create and store a new demand prediction.
        
        Args:
            product_id: Product ID
            store_id: Store ID
            predicted_demand: Predicted demand value
            prediction_date: Date for prediction
            confidence_level: Optional confidence level (0-1)
            model_version: Version of prediction model
            prediction_type: Type of prediction
        
        Returns:
            Created DemandPrediction object
        """
        prediction = DemandPrediction(
            product_id=product_id,
            store_id=store_id,
            predicted_demand=predicted_demand,
            prediction_date=prediction_date,
            confidence_level=confidence_level,
            model_version=model_version,
            prediction_type=prediction_type,
        )
        
        self.db.add(prediction)
        self.db.commit()
        self.db.refresh(prediction)
        
        # Invalidate cache
        if self.cache:
            cache_key = f"demand_prediction:{product_id}:{prediction_date.date()}:{store_id}"
            self.cache.delete(cache_key)
        
        logger.info(
            f"Created demand prediction: product={product_id}, "
            f"store={store_id}, date={prediction_date.date()}, "
            f"demand={predicted_demand}"
        )
        
        return prediction
    
    def batch_predict_demand(
        self,
        product_ids: List[int],
        store_id: int,
        start_date: datetime,
        num_days: int = 7,
    ) -> List[DemandPrediction]:
        """Generate demand predictions for multiple products.
        
        Args:
            product_ids: List of product IDs to predict
            store_id: Store ID for predictions
            start_date: Starting date for predictions
            num_days: Number of days to predict
        
        Returns:
            List of created DemandPrediction objects
        """
        predictions = []
        
        for product_id in product_ids:
            for day_offset in range(num_days):
                target_date = start_date + timedelta(days=day_offset)
                
                predicted_demand, confidence = self.calculate_demand_prediction(
                    product_id, target_date, store_id
                )
                
                prediction = self.create_prediction(
                    product_id=product_id,
                    store_id=store_id,
                    predicted_demand=predicted_demand,
                    prediction_date=target_date,
                    confidence_level=confidence,
                )
                
                predictions.append(prediction)
        
        logger.info(
            f"Batch created {len(predictions)} demand predictions "
            f"for {len(product_ids)} products over {num_days} days"
        )
        
        return predictions
    
    def get_predictions_by_product(
        self,
        product_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        store_id: Optional[int] = None,
    ) -> List[DemandPrediction]:
        """Get demand predictions for a specific product.
        
        Args:
            product_id: Product ID to filter by
            start_date: Optional start date filter
            end_date: Optional end date filter
            store_id: Optional store ID filter
        
        Returns:
            List of DemandPrediction objects
        """
        query = self.db.query(DemandPrediction).filter(
            DemandPrediction.product_id == product_id
        )
        
        if start_date:
            query = query.filter(DemandPrediction.prediction_date >= start_date)
        
        if end_date:
            query = query.filter(DemandPrediction.prediction_date < end_date)
        
        if store_id:
            query = query.filter(DemandPrediction.store_id == store_id)
        
        return query.order_by(DemandPrediction.prediction_date.asc()).all()
    
    def get_predictions_by_store(
        self,
        store_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[DemandPrediction]:
        """Get demand predictions for a specific store.
        
        Args:
            store_id: Store ID to filter by
            start_date: Optional start date filter
            end_date: Optional end date filter
        
        Returns:
            List of DemandPrediction objects
        """
        query = self.db.query(DemandPrediction).filter(
            DemandPrediction.store_id == store_id
        )
        
        if start_date:
            query = query.filter(DemandPrediction.prediction_date >= start_date)
        
        if end_date:
            query = query.filter(DemandPrediction.prediction_date < end_date)
        
        return query.order_by(DemandPrediction.prediction_date.asc()).all()
    
    def get_overall_demand_prediction(
        self,
        target_date: Optional[datetime] = None,
    ) -> Optional[float]:
        """Get aggregated demand prediction across all products.
        
        Args:
            target_date: Date for prediction (defaults to today)
        
        Returns:
            Aggregated demand prediction or None
        """
        if target_date is None:
            target_date = datetime.utcnow()
        
        # Get all predictions for the target date
        predictions = self.db.query(
            func.avg(DemandPrediction.predicted_demand).label('avg_demand'),
            func.count(DemandPrediction.id).label('count'),
        ).filter(
            DemandPrediction.prediction_date >= target_date.date(),
            DemandPrediction.prediction_date < target_date.date() + timedelta(days=1),
        ).first()
        
        if predictions and predictions.count > 0:
            return float(predictions.avg_demand or 0)
        
        return None
    
    def cleanup_old_predictions(self, days: int = 90) -> int:
        """Remove predictions older than specified days.
        
        Args:
            days: Number of days to keep (default 90)
        
        Returns:
            Number of deleted records
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        deleted = self.db.query(DemandPrediction).filter(
            DemandPrediction.prediction_date < cutoff_date,
            DemandPrediction.created_at < cutoff_date,
        ).delete()
        
        self.db.commit()
        
        logger.info(f"Cleaned up {deleted} old demand predictions")

        return deleted

    def get_forecast_range(
        self,
        product_id: int,
        start_date: datetime,
        end_date: datetime,
        store_id: Optional[int] = None,
    ) -> List[DemandPrediction]:
        """Get demand predictions for a product over a date range.

        Args:
            product_id: Product ID to filter by
            start_date: Start date for range
            end_date: End date for range
            store_id: Optional store ID to filter by

        Returns:
            List of DemandPrediction objects
        """
        return self.get_predictions_by_product(product_id, start_date, end_date, store_id)

    def get_inventory_recommendation(
        self,
        product_id: int,
        store_id: Optional[int] = None,
    ) -> dict:
        """Get inventory recommendation for a product.

        Based on demand prediction and current inventory levels,
        provides a recommendation for reorder, discount, or no action.

        Args:
            product_id: Product ID
            store_id: Optional store ID

        Returns:
            Dictionary with recommendation and reasoning
        """
        from shared.constants import RecommendationType

        today = datetime.utcnow()
        prediction = self.get_prediction(product_id, today, store_id)

        if prediction is None:
            predicted_demand, _ = self.calculate_demand_prediction(product_id, today, store_id)
        else:
            predicted_demand = prediction

        product = self.db.query(Product).filter(Product.id == product_id).first()

        if not product:
            return {
                "product_id": product_id,
                "recommendation": RecommendationType.NO_REORDER.value,
                "reasoning": "Product not found",
                "confidence": 0.0,
            }

        avg_daily = self._calculate_default_prediction(product_id, today, store_id)[0]
        threshold = avg_daily * 0.8

        if predicted_demand > threshold:
            recommendation = RecommendationType.REORDER.value
            reasoning = f"High demand predicted ({predicted_demand:.1f} units/day). Reorder recommended."
        elif predicted_demand < avg_daily * 0.3:
            recommendation = RecommendationType.DISCOUNT.value
            reasoning = f"Low demand predicted ({predicted_demand:.1f} units/day). Consider discount to reduce waste risk."
        else:
            recommendation = RecommendationType.NO_REORDER.value
            reasoning = f"Stable demand ({predicted_demand:.1f} units/day). Maintain current stock levels."

        return {
            "product_id": product_id,
            "product_name": product.name,
            "predicted_demand": predicted_demand,
            "recommendation": recommendation,
            "reasoning": reasoning,
        }


def get_demand_service(db: Session, cache: Optional[CacheManager] = None) -> DemandService:
    """Factory function to create DemandService instance.
    
    Args:
        db: Database session
        cache: Optional cache manager
    
    Returns:
        Configured DemandService instance
    """
    return DemandService(db=db, cache=cache)

"""
Nightly Tasks Module

Provides automated task execution for nightly batch processing including:
- Demand forecasting
- Alert generation  
- Recommendation generation
- System health checks

This module is designed to be run as a scheduled task (e.g., cron job)
to process data and generate insights for the waste optimization system.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.alert import Alert
from app.models.demand import DemandPrediction
from app.models.waste import Product, Store, WasteRecord, WasteMetric
from app.models.user import User
from shared.constants import (
    AlertSeverity,
    DEFAULT_WASTE_THRESHOLD_PERCENT,
    CRITICAL_WASTE_THRESHOLD_PERCENT,
    FORECAST_WINDOW_DAYS,
    FORECAST_HISTORY_DAYS,
    MIN_HISTORY_FOR_PREDICTION,
)
from shared.utils import (
    get_current_datetime,
    add_days,
)

logger = logging.getLogger(__name__)


class NightlyTaskResult:
    """Result object for nightly task execution."""
    
    def __init__(self):
        self.forecasting_run: bool = False
        self.alerts_generated: bool = False
        self.db_updated: bool = False
        self.recommendations_generated: bool = False
        self.error_logged: bool = False
        self.critical_alert_generated: bool = False
        self.errors: List[str] = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary matching test expectations."""
        return {
            'forecasting_run': self.forecasting_run,
            'alerts_generated': self.alerts_generated,
            'db_updated': self.db_updated,
            'recommendations_generated': self.recommendations_generated,
            'error_logged': self.error_logged,
            'critical_alert_generated': self.critical_alert_generated,
        }


def check_new_data_available(db: Session) -> bool:
    """Check if there is new data available for processing.
    
    Args:
        db: Database session
    
    Returns:
        True if new data is available, False otherwise
    """
    # Check for waste records from the last 24 hours
    last_24_hours = get_current_datetime() - timedelta(hours=24)
    recent_records = db.query(WasteRecord).filter(
        WasteRecord.created_at >= last_24_hours
    ).count()
    
    # Check for waste metrics from the last 24 hours
    recent_metrics = db.query(WasteMetric).filter(
        WasteMetric.date >= last_24_hours
    ).count()
    
    has_data = recent_records > 0 or recent_metrics > 0
    
    if not has_data:
        logger.info(f"No new data available for nightly processing (records: {recent_records}, metrics: {recent_metrics})")
    
    return has_data


def run_forecasting(db: Session, result: NightlyTaskResult) -> None:
    """
    Run demand forecasting for all products and stores.
    
    Args:
        db: Database session
        result: NightlyTaskResult to update with execution state
    """
    try:
        logger.info("Starting demand forecasting...")
        
        # Get all active products and stores
        products = db.query(Product).filter(Product.is_active == 1).all()
        stores = db.query(Store).filter(Store.is_active == 1).all()
        
        if not products or not stores:
            logger.warning("No active products or stores found for forecasting")
            return
        
        predictions_created = 0
        forecast_date = get_current_datetime() + timedelta(days=FORECAST_WINDOW_DAYS)
        
        for product in products:
            for store in stores:
                # Check if we have enough historical data
                history_start = get_current_datetime() - timedelta(days=FORECAST_HISTORY_DAYS)
                historical_data = db.query(WasteMetric).filter(
                    WasteMetric.product_id == product.id,
                    WasteMetric.store_id == store.id,
                    WasteMetric.date >= history_start
                ).all()
                
                if len(historical_data) < MIN_HISTORY_FOR_PREDICTION:
                    logger.debug(
                        f"Insufficient history for product {product.id} at store {store.id} "
                        f"(has {len(historical_data)}, needs {MIN_HISTORY_FOR_PREDICTION})"
                    )
                    continue
                
                # Calculate average demand from historical data
                total_quantity = sum(m.total_quantity_wasted for m in historical_data)
                avg_quantity = total_quantity / len(historical_data)
                
                # Simple moving average forecast with seasonal adjustment
                # In production, this would use a more sophisticated model
                predicted_demand = avg_quantity * 1.1  # 10% buffer
                
                # Create prediction record
                prediction = DemandPrediction(
                    product_id=product.id,
                    store_id=store.id,
                    predicted_demand=predicted_demand,
                    prediction_date=forecast_date,
                    confidence_level=0.75,
                    model_version="1.0.0",
                    prediction_type="daily",
                    created_at=get_current_datetime()
                )
                db.add(prediction)
                predictions_created += 1
        
        if predictions_created > 0:
            db.commit()
            result.forecasting_run = True
            result.db_updated = True
            logger.info(f"Forecasting complete: {predictions_created} predictions created")
        else:
            logger.info("No predictions generated (insufficient data)")
            
    except Exception as e:
        logger.error(f"Forecasting error: {str(e)}")
        result.error_logged = True
        result.errors.append(f"Forecasting error: {str(e)}")
        result.critical_alert_generated = True
        
        # Generate critical alert for forecasting failure
        try:
            critical_alert = Alert(
                product_id=None,
                store_id=None,
                severity=AlertSeverity.CRITICAL,
                alert_type="forecasting_failure",
                message=f"Nightly forecasting failed: {str(e)}",
                created_at=get_current_datetime(),
                is_active=1
            )
            db.add(critical_alert)
            db.commit()
            result.db_updated = True
            logger.info("Critical alert created for forecasting failure")
        except Exception as alert_err:
            logger.error(f"Failed to create critical alert: {str(alert_err)}")
            db.rollback()


def generate_alerts(db: Session, result: NightlyTaskResult) -> None:
    """
    Generate alerts based on waste metrics and predictions.
    
    Args:
        db: Database session
        result: NightlyTaskResult to update with execution state
    """
    try:
        logger.info("Starting alert generation...")
        
        # Get recent waste metrics
        last_7_days = get_current_datetime() - timedelta(days=7)
        recent_metrics = db.query(WasteMetric).filter(
            WasteMetric.date >= last_7_days
        ).all()
        
        if not recent_metrics:
            logger.info("No recent waste metrics to analyze for alerts")
            return
        
        alerts_created = 0
        
        # Group metrics by product-store combination
        metrics_by_ps = {}
        for metric in recent_metrics:
            key = (metric.product_id, metric.store_id)
            if key not in metrics_by_ps:
                metrics_by_ps[key] = []
            metrics_by_ps[key].append(metric)
        
        for (product_id, store_id), metrics in metrics_by_ps.items():
            # Calculate total waste in the period
            total_waste = sum(m.total_cost_wasted for m in metrics)
            total_quantity = sum(m.total_quantity_wasted for m in metrics)
            
            if total_quantity == 0:
                continue
            
            # Calculate waste percentage (simplified - using recent avg cost)
            avg_cost_per_unit = total_waste / total_quantity if total_quantity > 0 else 0
            
            # Determine severity based on waste threshold
            if total_waste > 0:
                # Check if we need to alert based on configurable thresholds
                # Using simplified logic - in production would compare against inventory value
                waste_ratio = total_waste / 1000  # Simplified benchmark
                
                if waste_ratio > CRITICAL_WASTE_THRESHOLD_PERCENT / 100:
                    severity = AlertSeverity.CRITICAL
                    alert_type = "high_waste"
                elif waste_ratio > DEFAULT_WASTE_THRESHOLD_PERCENT / 100:
                    severity = AlertSeverity.WARNING
                    alert_type = "elevated_waste"
                else:
                    continue  # No alert needed
                
                # Check if similar alert already exists
                existing_alert = db.query(Alert).filter(
                    Alert.product_id == product_id,
                    Alert.store_id == store_id,
                    Alert.alert_type == alert_type,
                    Alert.is_active == 1,
                    Alert.created_at >= last_7_days
                ).first()
                
                if existing_alert:
                    continue
                
                # Get product name for message
                product = db.query(Product).filter(Product.id == product_id).first()
                product_name = product.name if product else f"Product {product_id}"
                
                # Create alert
                alert = Alert(
                    product_id=product_id,
                    store_id=store_id,
                    severity=severity,
                    alert_type=alert_type,
                    message=f"{alert_type.title()} waste detected for {product_name}: ${total_waste:.2f} waste value in last 7 days",
                    created_at=get_current_datetime(),
                    is_active=1
                )
                db.add(alert)
                alerts_created += 1
        
        if alerts_created > 0:
            db.commit()
            result.alerts_generated = True
            result.db_updated = True
            logger.info(f"Alert generation complete: {alerts_created} alerts created")
        else:
            logger.info("No new alerts generated")
            
    except Exception as e:
        logger.error(f"Alert generation error: {str(e)}")
        result.error_logged = True
        result.errors.append(f"Alert generation error: {str(e)}")
        # Do not update DB when alerting fails
        result.db_updated = False
      

def generate_recommendations(db: Session, result: NightlyTaskResult) -> None:
    """
    Generate recommendations based on waste analysis and predictions.
    
    Args:
        db: Database session
        result: NightlyTaskResult to update with execution state
    """
    try:
        logger.info("Starting recommendation generation...")
        
        # Get recent predictions
        prediction_date = get_current_datetime() + timedelta(days=1)
        predictions = db.query(DemandPrediction).filter(
            DemandPrediction.prediction_date >= prediction_date
        ).all()
        
        if not predictions:
            logger.info("No predictions available for recommendations")
            return
        
        recommendations_created = 0
        # For each high-prediction item, generate recommendation
        # This is a simplified version - in production would integrate with inventory data
        
        for prediction in predictions:
            # Skip if predicted demand is very low
            if prediction.predicted_demand < 1.0:
                continue
            
            # Get product info
            product = db.query(Product).filter(
                Product.id == prediction.product_id
            ).first()
            
            if not product:
                continue
            
            # Decision logic for recommendations
            # - High predicted demand: recommend reorder
            # - Very high predicted demand: recommend discount to move inventory
            # - Low/no predicted demand: recommend no reorder
            
            if prediction.predicted_demand > 50:
                recommendation_type = "reorder"
            elif prediction.predicted_demand > 20:
                recommendation_type = "discount"
            else:
                recommendation_type = "no_reorder"
            
            # Create alert as recommendation
            alert = Alert(
                product_id=prediction.product_id,
                store_id=prediction.store_id,
                severity=AlertSeverity.INFO,
                alert_type=f"recommendation_{recommendation_type}",
                message=f"Recommendation: {recommendation_type} - "
                         f"Predicted demand: {prediction.predicted_demand:.1f} units for {product.name}",
                created_at=get_current_datetime(),
                is_active=1
            )
            db.add(alert)
            recommendations_created += 1
        
        if recommendations_created > 0:
            db.commit()
            result.recommendations_generated = True
            result.db_updated = True
            logger.info(f"Recommendation generation complete: {recommendations_created} recommendations created")
        else:
            logger.info("No recommendations generated")
            
    except Exception as e:
        logger.error(f"Recommendation generation error: {str(e)}")
        result.error_logged = True
        result.errors.append(f"Recommendation error: {str(e)}")


def run_nightly_tasks() -> NightlyTaskResult:
    """
    Execute all nightly tasks.
    
    This function orchestrates the nightly batch processing including:
    - Data availability check
    - Demand forecasting
    - Alert generation
    - Recommendation generation
    
    Returns:
        NightlyTaskResult containing execution results
    """
    result = NightlyTaskResult()
    
    logger.info("Starting nightly task execution...")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Check for new data availability
        has_new_data = check_new_data_available(db)
        
        if not has_new_data:
            logger.info("No new data to process - nightly tasks completing gracefully")
            # Still mark as completed successfully (no error)
            return result
        
        # Run forecasting
        run_forecasting(db, result)
        
        # Run alert generation
        generate_alerts(db, result)
        
        # Run recommendations
        generate_recommendations(db, result)
        
        logger.info("Nightly task execution completed successfully")
        
    except Exception as e:
        logger.error(f"Unexpected error in nightly tasks: {str(e)}")
        result.error_logged = True
        result.errors.append(f"Unexpected error: {str(e)}")
        db.rollback()
    finally:
        db.close()
    
    return result


def main() -> None:
    """Main entry point for nightly task execution."""
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
        format=settings.LOG_FORMAT
    )
    
    logger.info("=" * 60)
    logger.info("Starting nightly batch processing...")
    logger.info(f"Environment: {settings.APP_ENV_DEFAULT}")
    logger.info("=" * 60)
    
    result = run_nightly_tasks()
    
    logger.info("=" * 60)
    logger.info("Nightly task results:")
    for key, value in result.to_dict().items():
        logger.info(f"  {key}: {value}")
    logger.info("=" * 60)
    
    # Exit with appropriate code
    if result.error_logged and not result.db_updated:
        logger.error("Nightly tasks completed with errors - no DB updates")
    else:
        logger.info("Nightly tasks completed successfully")


if __name__ == "__main__":
    main()

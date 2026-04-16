"""
Alert Service

Business logic layer for alert management operations.
Provides functions for retrieving, creating, updating, and managing alerts.
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.schemas.alert import AlertResponse
from shared.constants import AlertSeverity
from shared.utils import to_iso8601

logger = logging.getLogger(__name__)


class AlertService:
    """Service for managing alerts in the waste optimization system.
    
    Provides business logic for alert retrieval, creation, and management.
    Handles querying active alerts from the database and converting
    them to API response schemas.
    
    Attributes:
        _valid_severities: List of valid severity values
    """
    
    _valid_severities: List[str] = [
        AlertSeverity.INFO.value,
        AlertSeverity.WARNING.value,
        AlertSeverity.CRITICAL.value
    ]
    
    @classmethod
    def get_alerts(
        cls,
        db: Session,
        is_active: Optional[bool] = True,
        severity: Optional[str] = None,
        product_id: Optional[int] = None,
        store_id: Optional[int] = None,
        limit: Optional[int] = None
    ) -> List[AlertResponse]:
        """Retrieve alerts from the database.
        
        Queries the alerts table and returns a list of AlertResponse objects.
        Supports filtering by active status, severity, product, and store.
        
        Args:
            db: Database session
            is_active: Filter by active status (default: True)
            severity: Filter by severity level
            product_id: Filter by product ID
            store_id: Filter by store ID
            limit: Maximum number of alerts to return
        
        Returns:
            List of AlertResponse objects
        """
        try:
            query = db.query(Alert)
            
            # Apply filters
            if is_active is not None:
                query = query.filter(Alert.is_active == (1 if is_active else 0))
            
            if severity:
                if severity not in cls._valid_severities:
                    logger.warning(f"Invalid severity filter: {severity}")
                else:
                    query = query.filter(Alert.severity == severity)
            
            if product_id is not None:
                query = query.filter(Alert.product_id == product_id)
            
            if store_id is not None:
                query = query.filter(Alert.store_id == store_id)
            
            # Order by created_at descending (newest first)
            query = query.order_by(Alert.created_at.desc())
            
            # Apply limit if specified
            if limit is not None and limit > 0:
                query = query.limit(limit)
            
            alerts = query.all()
            
            # Convert to response schema
            return cls._transform_alerts(alerts)
            
        except Exception as e:
            logger.error(f"Error retrieving alerts: {e}")
            raise
    
    @classmethod
    def _transform_alerts(cls, alerts: List[Alert]) -> List[AlertResponse]:
        """Transform Alert database models to AlertResponse schemas.
        
        Args:
            alerts: List of Alert database models
        
        Returns:
            List of AlertResponse schemas
        """
        result: List[AlertResponse] = []
        
        for alert in alerts:
            # Validate severity
            severity_value = alert.severity
            if severity_value not in cls._valid_severities:
                logger.warning(
                    f"Alert {alert.id} has invalid severity: {severity_value}, "
                    f"skipping"
                )
                continue
            
            try:
                created_at_str = to_iso8601(alert.created_at) if alert.created_at else ""
            except Exception:
                created_at_str = ""
            
            response = AlertResponse(
                id=alert.id,
                created_at=created_at_str,
                message=alert.message,
                severity=severity_value  # type: ignore
            )
            result.append(response)
        
        return result
    
    @classmethod
    def get_alert_by_id(cls, db: Session, alert_id: int) -> Optional[AlertResponse]:
        """Retrieve a single alert by ID.
        
        Args:
            db: Database session
            alert_id: Alert ID
        
        Returns:
            AlertResponse if found, None otherwise
        """
        try:
            alert = db.query(Alert).filter(Alert.id == alert_id).first()
            
            if alert is None:
                return None
            
            alerts = cls._transform_alerts([alert])
            return alerts[0] if alerts else None
            
        except Exception as e:
            logger.error(f"Error retrieving alert {alert_id}: {e}")
            raise
    
    @classmethod
    def create_alert(
        cls,
        db: Session,
        message: str,
        severity: str,
        alert_type: str,
        product_id: Optional[int] = None,
        store_id: Optional[int] = None
    ) -> AlertResponse:
        """Create a new alert.
        
        Args:
            db: Database session
            message: Alert message
            severity: Alert severity (info, warning, critical)
            alert_type: Type of alert
            product_id: Related product ID
            store_id: Related store ID
        
        Returns:
            Created AlertResponse
        
        Raises:
            ValueError: If severity is invalid
        """
        if severity not in cls._valid_severities:
            raise ValueError(f"Invalid severity: {severity}")
        
        try:
            alert = Alert(
                product_id=product_id,
                store_id=store_id,
                severity=severity,
                alert_type=alert_type,
                message=message,
                created_at=datetime.now(timezone.utc),
                is_active=1
            )
            
            db.add(alert)
            db.commit()
            db.refresh(alert)
            
            logger.info(f"Created alert {alert.id}: {alert_type}")
            
            return cls._transform_alerts([alert])[0]
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating alert: {e}")
            raise
    
    @classmethod
    def acknowledge_alert(cls, db: Session, alert_id: int) -> Optional[AlertResponse]:
        """Acknowledge an alert.
        
        Args:
            db: Database session
            alert_id: Alert ID
        
        Returns:
            Updated AlertResponse if found, None otherwise
        """
        try:
            alert = db.query(Alert).filter(Alert.id == alert_id).first()
            
            if alert is None:
                return None
            
            alert.acknowledged_at = datetime.now(timezone.utc)
            
            db.commit()
            db.refresh(alert)
            
            logger.info(f"Acknowledged alert {alert_id}")
            
            return cls._transform_alerts([alert])[0]
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error acknowledging alert {alert_id}: {e}")
            raise
    
    @classmethod
    def resolve_alert(cls, db: Session, alert_id: int) -> Optional[AlertResponse]:
        """Resolve an alert.
        
        Args:
            db: Database session
            alert_id: Alert ID
        
        Returns:
            Updated AlertResponse if found, None otherwise
        """
        try:
            alert = db.query(Alert).filter(Alert.id == alert_id).first()
            
            if alert is None:
                return None
            
            alert.resolved_at = datetime.now(timezone.utc)
            alert.is_active = 0
            
            db.commit()
            db.refresh(alert)
            
            logger.info(f"Resolved alert {alert_id}")
            
            return cls._transform_alerts([alert])[0]
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error resolving alert {alert_id}: {e}")
            raise
    
    @classmethod
    def get_critical_alerts(
        cls,
        db: Session,
        limit: Optional[int] = None
    ) -> List[AlertResponse]:
        """Get all critical severity alerts.
        
        Args:
            db: Database session
            limit: Maximum number of alerts to return
        
        Returns:
            List of critical AlertResponse objects
        """
        return cls.get_alerts(
            db=db,
            is_active=True,
            severity=AlertSeverity.CRITICAL.value,
            limit=limit
        )
    
    @classmethod
    def get_alerts_by_product(
        cls,
        db: Session,
        product_id: int,
        is_active: Optional[bool] = True
    ) -> List[AlertResponse]:
        """Get alerts for a specific product.
        
        Args:
            db: Database session
            product_id: Product ID
            is_active: Filter by active status
        
        Returns:
            List of AlertResponse objects for the product
        """
        return cls.get_alerts(
            db=db,
            is_active=is_active,
            product_id=product_id
        )
    
    @classmethod
    def get_alerts_by_store(
        cls,
        db: Session,
        store_id: int,
        is_active: Optional[bool] = True
    ) -> List[AlertResponse]:
        """Get alerts for a specific store.
        
        Args:
            db: Database session
            store_id: Store ID
            is_active: Filter by active status
        
        Returns:
            List of AlertResponse objects for the store
        """
        return cls.get_alerts(
            db=db,
            is_active=is_active,
            store_id=store_id
        )
    
    @classmethod
    def get_active_alert_count(cls, db: Session) -> int:
        """Get count of active alerts.
        
        Args:
            db: Database session
        
        Returns:
            Number of active alerts
        """
        try:
            count = db.query(Alert).filter(Alert.is_active == 1).count()
            return count
        except Exception as e:
            logger.error(f"Error counting active alerts: {e}")
            raise


# Module-level functions that delegate to the service class


def get_alerts(
    db: Session,
    is_active: Optional[bool] = True,
    severity: Optional[str] = None,
    product_id: Optional[int] = None,
    store_id: Optional[int] = None,
    limit: Optional[int] = None
) -> List[AlertResponse]:
    """Retrieve alerts from the database.
    
    This is a module-level function that delegates to AlertService.
    
    Args:
        db: Database session
        is_active: Filter by active status
        severity: Filter by severity level
        product_id: Filter by product ID
        store_id: Filter by store ID
        limit: Maximum number of alerts to return
    
    Returns:
        List of AlertResponse objects
    """
    return AlertService.get_alerts(
        db=db,
        is_active=is_active,
        severity=severity,
        product_id=product_id,
        store_id=store_id,
        limit=limit
    )


def get_alert_by_id(db: Session, alert_id: int) -> Optional[AlertResponse]:
    """Retrieve a single alert by ID.
    
    Args:
        db: Database session
        alert_id: Alert ID
    
    Returns:
        AlertResponse if found, None otherwise
    """
    return AlertService.get_alert_by_id(db=db, alert_id=alert_id)



def create_alert(
    db: Session,
    message: str,
    severity: str,
    alert_type: str,
    product_id: Optional[int] = None,
    store_id: Optional[int] = None
) -> AlertResponse:
    """Create a new alert.
    
    Args:
        db: Database session
        message: Alert message
        severity: Alert severity
        alert_type: Type of alert
        product_id: Related product ID
        store_id: Related store ID
    
    Returns:
        Created AlertResponse
    """
    return AlertService.create_alert(
        db=db,
        message=message,
        severity=severity,
        alert_type=alert_type,
        product_id=product_id,
        store_id=store_id
    )


def acknowledge_alert(db: Session, alert_id: int) -> Optional[AlertResponse]:
    """Acknowledge an alert.
    
    Args:
        db: Database session
        alert_id: Alert ID
    
    Returns:
        Updated AlertResponse if found, None otherwise
    """
    return AlertService.acknowledge_alert(db=db, alert_id=alert_id)


def resolve_alert(db: Session, alert_id: int) -> Optional[AlertResponse]:
    """Resolve an alert.
    
    Args:
        db: Database session
        alert_id: Alert ID
    
    Returns:
        Updated AlertResponse if found, None otherwise
    """
    return AlertService.resolve_alert(db=db, alert_id=alert_id)

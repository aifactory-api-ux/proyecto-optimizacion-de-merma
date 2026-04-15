"""
Alerts API Endpoint

Provides REST API endpoints for alert management including
retrieving, creating, updating, and acknowledging alerts.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import verify_token_and_get_user_id
from app.db.session import get_db
from app.models.alert import Alert
from app.schemas.alert import AlertResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/alerts", tags=["alerts"])


def get_current_user_from_token(
    authorization: Optional[str] = None
) -> int:
    """Extract and validate user ID from Authorization header.
    
    Args:
        authorization: Authorization header with Bearer token
        
    Returns:
        User ID from the token
        
    Raises:
        HTTPException: If token is missing, invalid, or expired
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is required"
        )
    
    # Extract token from "Bearer <token>" format
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
    
    token = parts[1]
    user_id = verify_token_and_get_user_id(token)
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return user_id


@router.get("", response_model=List[AlertResponse])
def get_alerts(
    db: Session = Depends(get_db),
    authorization: Optional[str] = None,
    severity: Optional[str] = None,
    alert_type: Optional[str] = None,
    is_active: bool = True,
) -> List[AlertResponse]:
    """Retrieve all alerts with optional filtering.
    
    Args:
        db: Database session
        authorization: Authorization header with Bearer token
        severity: Optional filter by severity level
        alert_type: Optional filter by alert type
        is_active: Filter by active status (default: True)
        
    Returns:
        List of AlertResponse objects
        
    Raises:
        HTTPException: If authorization is missing or invalid
    """
    # Validate authentication
    get_current_user_from_token(authorization)
    
    # Build query with filters
    query = db.query(Alert)
    
    # Apply filters
    if is_active is not None:
        query = query.filter(Alert.is_active == (1 if is_active else 0))
    
    if severity:
        # Validate severity values
        valid_severities = ["info", "warning", "critical"]
        if severity.lower() not in valid_severities:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid severity. Must be one of: {', '.join(valid_severities)}"
            )
        query = query.filter(Alert.severity == severity.lower())
    
    if alert_type:
        query = query.filter(Alert.alert_type == alert_type)
    
    # Order by created_at descending (most recent first)
    alerts = query.order_by(Alert.created_at.desc()).all()
    
    # Convert to response format
    return [
        AlertResponse(
            id=alert.id,
            created_at=alert.created_at.isoformat() if alert.created_at else None,
            message=alert.message,
            severity=alert.severity,
            product_id=alert.product_id,
            store_id=alert.store_id,
            alert_type=alert.alert_type,
            acknowledged_at=alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
            resolved_at=alert.resolved_at.isoformat() if alert.resolved_at else None,
            is_active=bool(alert.is_active),
        )
        for alert in alerts
    ]


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert_by_id(
    alert_id: int,
    db: Session = Depends(get_db),
    authorization: Optional[str] = None,
) -> AlertResponse:
    """Retrieve a specific alert by ID.
    
    Args:
        alert_id: The ID of the alert to retrieve
        db: Database session
        authorization: Authorization header with Bearer token
        
    Returns:
        AlertResponse object
        
    Raises:
        HTTPException: If authorization is missing/invalid or alert not found
    """
    # Validate authentication
    get_current_user_from_token(authorization)
    
    # Fetch alert
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found"
        )
    
    return AlertResponse(
        id=alert.id,
        created_at=alert.created_at.isoformat() if alert.created_at else None,
        message=alert.message,
        severity=alert.severity,
        product_id=alert.product_id,
        store_id=alert.store_id,
        alert_type=alert.alert_type,
        acknowledged_at=alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
        resolved_at=alert.resolved_at.isoformat() if alert.resolved_at else None,
        is_active=bool(alert.is_active),
    )


@router.post("", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
def create_alert(
    alert_data: dict,
    db: Session = Depends(get_db),
    authorization: Optional[str] = None,
) -> AlertResponse:
    """Create a new alert.
    
    Args:
        alert_data: Alert creation data
        db: Database session
        authorization: Authorization header with Bearer token
        
    Returns:
        Created AlertResponse object
        
    Raises:
        HTTPException: If authorization is missing/invalid or validation fails
    """
    # Validate authentication
    user_id = get_current_user_from_token(authorization)
    
    # Validate required fields
    if "message" not in alert_data or not alert_data["message"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message field is required"
        )
    
    if "severity" not in alert_data or not alert_data["severity"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Severity field is required"
        )
    
    # Validate severity value
    valid_severities = ["info", "warning", "critical"]
    if alert_data["severity"].lower() not in valid_severities:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid severity. Must be one of: {', '.join(valid_severities)}"
        )
    
    # Create new alert
    from datetime import datetime
    
    new_alert = Alert(
        product_id=alert_data.get("product_id"),
        store_id=alert_data.get("store_id"),
        severity=alert_data["severity"].lower(),
        alert_type=alert_data.get("alert_type", "general"),
        message=alert_data["message"],
        is_active=1,
    )
    
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)
    
    logger.info(f"Alert created: ID={new_alert.id}, severity={new_alert.severity}, user_id={user_id}")
    
    return AlertResponse(
        id=new_alert.id,
        created_at=new_alert.created_at.isoformat() if new_alert.created_at else None,
        message=new_alert.message,
        severity=new_alert.severity,
        product_id=new_alert.product_id,
        store_id=new_alert.store_id,
        alert_type=new_alert.alert_type,
        acknowledged_at=None,
        resolved_at=None,
        is_active=True,
    )


@router.patch("/{alert_id}/acknowledge", response_model=AlertResponse)
def acknowledge_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    authorization: Optional[str] = None,
) -> AlertResponse:
    """Acknowledge an alert.
    
    Args:
        alert_id: The ID of the alert to acknowledge
        db: Database session
        authorization: Authorization header with Bearer token
        
    Returns:
        Updated AlertResponse object
        
    Raises:
        HTTPException: If authorization is missing/invalid or alert not found
    """
    # Validate authentication
    user_id = get_current_user_from_token(authorization)
    
    # Fetch alert
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found"
        )
    
    # Update acknowledgment
    from datetime import datetime
    alert.acknowledged_at = datetime.utcnow()
    
    db.commit()
    db.refresh(alert)
    
    logger.info(f"Alert acknowledged: ID={alert_id}, user_id={user_id}")
    
    return AlertResponse(
        id=alert.id,
        created_at=alert.created_at.isoformat() if alert.created_at else None,
        message=alert.message,
        severity=alert.severity,
        product_id=alert.product_id,
        store_id=alert.store_id,
        alert_type=alert.alert_type,
        acknowledged_at=alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
        resolved_at=alert.resolved_at.isoformat() if alert.resolved_at else None,
        is_active=bool(alert.is_active),
    )


@router.patch("/{alert_id}/resolve", response_model=AlertResponse)
def resolve_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    authorization: Optional[str] = None,
) -> AlertResponse:
    """Resolve an alert.
    
    Args:
        alert_id: The ID of the alert to resolve
        db: Database session
        authorization: Authorization header with Bearer token
        
    Returns:
        Updated AlertResponse object
        
    Raises:
        HTTPException: If authorization is missing/invalid or alert not found
    """
    # Validate authentication
    user_id = get_current_user_from_token(authorization)
    
    # Fetch alert
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found"
        )
    
    # Update resolution
    from datetime import datetime
    alert.resolved_at = datetime.utcnow()
    alert.is_active = 0
    
    db.commit()
    db.refresh(alert)
    
    logger.info(f"Alert resolved: ID={alert_id}, user_id={user_id}")
    
    return AlertResponse(
        id=alert.id,
        created_at=alert.created_at.isoformat() if alert.created_at else None,
        message=alert.message,
        severity=alert.severity,
        product_id=alert.product_id,
        store_id=alert.store_id,
        alert_type=alert.alert_type,
        acknowledged_at=alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
        resolved_at=alert.resolved_at.isoformat() if alert.resolved_at else None,
        is_active=bool(alert.is_active),
    )

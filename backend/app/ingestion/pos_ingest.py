"""
POS Ingestion Module

Provides functionality for ingesting Point of Sale (POS) data into the waste
optimization system. Handles validation, transformation, and storage of
POS transaction records.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.waste import Product, Store, WasteRecord
from app.db.session import get_db_session

logger = logging.getLogger(__name__)


class POSDataValidator:
    """Validator for POS data ingestion payloads."""
    
    REQUIRED_FIELDS = [
        "product_id",
        "store_id",
        "quantity_sold",
        "sale_date"
    ]
    
    NUMERIC_FIELDS = [
        "product_id",
        "store_id",
        "quantity_sold",
        "unit_price"
    ]
    
    @staticmethod
    def validate_payload(payload: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate a POS data payload.
        
        Args:
            payload: Dictionary containing POS data fields
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not payload:
            return False, "Empty payload provided"
        
        # Check required fields
        missing_fields = []
        for field in POSDataValidator.REQUIRED_FIELDS:
            if field not in payload or payload[field] is None:
                missing_fields.append(field)
        
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"
        
        # Validate numeric fields
        for field in POSDataValidator.NUMERIC_FIELDS:
            if field in payload and payload[field] is not None:
                if not isinstance(payload[field], (int, float)):
                    return False, f"Invalid data type for field '{field}': expected number, got {type(payload[field]).__name__}"
        
        return True, None
    
    @staticmethod
    def validate_field_types(payload: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate that all fields have appropriate types.
        
        Args:
            payload: Dictionary containing POS data fields
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        for field in POSDataValidator.NUMERIC_FIELDS:
            if field in payload and payload[field] is not None:
                if isinstance(payload[field], str):
                    try:
                        float(payload[field])
                    except ValueError:
                        return False, f"Invalid data type for field '{field}': cannot convert to number"
        
        return True, None


class POSIngestionService:
    """Service for ingesting POS data into the system."""
    
    def __init__(self, db_session: Session):
        """Initialize POS ingestion service.
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db_session = db_session
        self.validator = POSDataValidator()
    
    def _parse_sale_date(self, sale_date: Any) -> Optional[datetime]:
        """Parse sale_date from various formats.
        
        Args:
            sale_date: Date string or datetime object
            
        Returns:
            Parsed datetime or None if invalid
        """
        if isinstance(sale_date, datetime):
            return sale_date
        
        if isinstance(sale_date, str):
            # Try ISO 8601 format first
            try:
                return datetime.fromisoformat(sale_date.replace('Z', '+00:00'))
            except ValueError:
                pass
            
            # Try other common formats
            formats = [
                "%Y-%m-%d",
                "%Y-%m-%d %H:%M:%S",
                "%Y/%m/%d",
                "%d/%m/%Y",
                "%m/%d/%Y"
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(sale_date, fmt)
                except ValueError:
                    continue
        
        return None
    
    def _validate_product_exists(self, product_id: int) -> bool:
        """Check if product exists in database.
        
        Args:
            product_id: Product ID to check
            
        Returns:
            True if product exists, False otherwise
        """
        stmt = select(Product).where(Product.id == product_id)
        result = self.db_session.execute(stmt).scalar_one_or_none()
        return result is not None
    
    def _validate_store_exists(self, store_id: int) -> bool:
        """Check if store exists in database.
        
        Args:
            store_id: Store ID to check
            
        Returns:
            True if store exists, False otherwise
        """
        stmt = select(Store).where(Store.id == store_id)
        result = self.db_session.execute(stmt).scalar_one_or_none()
        return result is not None
    
    def ingest_pos_record(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Ingest a single POS record into the system.
        
        Args:
            payload: Dictionary containing POS data fields
        Returns:
            Result dictionary with status and error (if any)
        """
        is_valid, error = self.validator.validate_payload(payload)
        if not is_valid:
            logger.error(f"POS ingestion validation failed: {error}")
            return {"status": "error", "error": error}
        
        # Validate product and store existence
        product_id = payload["product_id"]
        store_id = payload["store_id"]
        if not self._validate_product_exists(product_id):
            return {"status": "error", "error": f"Product ID {product_id} does not exist"}
        if not self._validate_store_exists(store_id):
            return {"status": "error", "error": f"Store ID {store_id} does not exist"}
        
        # Parse sale_date
        sale_date = self._parse_sale_date(payload["sale_date"])
        if sale_date is None:
            return {"status": "error", "error": "Invalid sale_date format"}
        
        # Insert record (minimal implementation)
        try:
            waste_record = WasteRecord(
                product_id=product_id,
                store_id=store_id,
                quantity=payload["quantity_sold"],
                sale_date=sale_date,
                unit_price=payload.get("unit_price", 0.0),
                created_at=datetime.utcnow()
            )
            self.db_session.add(waste_record)
            self.db_session.commit()
            return {"status": "success"}
        except IntegrityError as e:
            self.db_session.rollback()
            logger.error(f"Integrity error during POS ingestion: {e}")
            return {"status": "error", "error": "Database integrity error"}
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Unexpected error during POS ingestion: {e}")
            return {"status": "error", "error": str(e)}

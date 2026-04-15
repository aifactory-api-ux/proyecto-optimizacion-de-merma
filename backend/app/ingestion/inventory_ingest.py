"""
Inventory Ingestion Module

Provides functionality for ingesting inventory data from external systems
(ERP, inventory management systems, manual entry). Handles validation,
normalization, and storage of inventory records in the database.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.session import get_db
from app.models.waste import Product, Store
from shared.constants import HTTP_STATUS, ERROR_MESSAGES

logger = logging.getLogger(__name__)

# Create router for inventory ingestion endpoints
router = APIRouter(prefix="/ingestion", tags=["ingestion"])


class InventoryRecord(BaseModel):
    """Model for individual inventory record during ingestion.
    
    Attributes:
        product_sku: SKU of the product
        store_code: Code of the store
        quantity_in_stock: Current quantity in stock
        quantity_reserved: Quantity reserved for orders
        last_restock_date: Date of last restock
        minimum_stock: Minimum stock threshold
        maximum_stock: Maximum stock threshold
        reorder_point: Point at which reorder should be triggered
    """
    product_sku: str = Field(..., min_length=1, max_length=50, description="Product SKU")
    store_code: str = Field(..., min_length=1, max_length=20, description="Store code")
    quantity_in_stock: float = Field(..., description="Current quantity in stock")
    quantity_reserved: float = Field(default=0.0, description="Quantity reserved for orders")
    last_restock_date: Optional[str] = Field(default=None, description="Date of last restock (ISO 8601)")
    minimum_stock: float = Field(default=0.0, description="Minimum stock threshold")
    maximum_stock: float = Field(default=1000.0, description="Maximum stock threshold")
    reorder_point: float = Field(default=0.0, description="Point at which reorder should be triggered")
    
    @field_validator('quantity_in_stock')
    @classmethod
    def validate_quantity_in_stock(cls, v: float) -> float:
        """Validate that quantity_in_stock is non-negative."""
        if v < 0:
            raise ValueError('quantity_in_stock cannot be negative')
        return v
    
    @field_validator('quantity_reserved')
    @classmethod
    def validate_quantity_reserved(cls, v: float) -> float:
        """Validate that quantity_reserved is non-negative."""
        if v < 0:
            raise ValueError('quantity_reserved cannot be negative')
        return v
    
    @field_validator('minimum_stock')
    @classmethod
    def validate_minimum_stock(cls, v: float) -> float:
        """Validate that minimum_stock is non-negative."""
        if v < 0:
            raise ValueError('minimum_stock cannot be negative')
        return v
    
    @field_validator('maximum_stock')
    @classmethod
    def validate_maximum_stock(cls, v: float) -> float:
        """Validate that maximum_stock is non-negative."""
        if v < 0:
            raise ValueError('maximum_stock cannot be negative')
        return v
    
    @field_validator('reorder_point')
    @classmethod
    def validate_reorder_point(cls, v: float) -> float:
        """Validate that reorder_point is non-negative."""
        if v < 0:
            raise ValueError('reorder_point cannot be negative')
        return v


class InventoryIngestRequest(BaseModel):
    """Request model for bulk inventory ingestion.
    
    Attributes:
        records: List of inventory records to ingest
        source: Source of the inventory data (erp, manual, etc.)
        import_date: Date of the import
    """
    records: List[InventoryRecord] = Field(..., min_length=1, description="List of inventory records")
    source: str = Field(default="manual", description="Source of inventory data")
    import_date: Optional[str] = Field(default=None, description="Date of import (ISO 8601)")


class InventoryIngestResponse(BaseModel):
    """Response model for inventory ingestion.
    
    Attributes:
        status: Status of the ingestion
        records_created: Number of records created
        records_updated: Number of records updated
        duplicates_handled: Whether duplicates were handled
        errors: List of error messages if any
    """
    status: str
    records_created: int
    records_updated: int
    duplicates_handled: bool
    errors: List[str] = []


class InventoryStore(Base):
    """Inventory storage model - tracks inventory levels per product/store.
    
    This model stores the current inventory state for each product at each store.
    
    Attributes:
        id: Primary key
        product_id: Foreign key to products table
        store_id: Foreign key to stores table
        quantity_in_stock: Current quantity in stock
        quantity_reserved: Quantity reserved for orders
        last_restock_date: Date of last restock
        minimum_stock: Minimum stock threshold
        maximum_stock: Maximum stock threshold
        reorder_point: Point at which reorder should be triggered
        last_updated: Timestamp of last update
        created_at: Timestamp of record creation
    """
    from app.db.base import Base
    
    __tablename__ = "inventory"
    
    from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
    from sqlalchemy.orm import relationship
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    store_id = Column(
        Integer,
        ForeignKey("stores.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    quantity_in_stock = Column(Float, nullable=False, default=0.0)
    quantity_reserved = Column(Float, nullable=False, default=0.0)
    last_restock_date = Column(DateTime, nullable=True)
    minimum_stock = Column(Float, nullable=False, default=0.0)
    maximum_stock = Column(Float, nullable=False, default=1000.0)
    reorder_point = Column(Float, nullable=False, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    product = relationship("Product", back_populates="inventory")
    store = relationship("Store", back_populates="inventory")
    
    # Unique constraint for product/store combination
    __table_args__ = (
        Index('ix_inventory_product_store', 'product_id', 'store_id', unique=True),
    )


def get_or_create_product(db: Session, sku: str) -> Optional[Product]:
    """Get product by SKU or return None if not found.
    
    Args:
        db: Database session
        sku: Product SKU to look up
    
    Returns:
        Product object if found, None otherwise
    """
    return db.query(Product).filter(Product.sku == sku).first()


def get_or_create_store(db: Session, store_code: str) -> Optional[Store]:
    """Get store by code or return None if not found.
    
    Args:
        db: Database session
        store_code: Store code to look up
    
    Returns:
        Store object if found, None otherwise
    """
    return db.query(Store).filter(Store.store_code == store_code).first()


def find_existing_inventory(db: Session, product_id: int, store_id: int) -> Optional[InventoryStore]:
    """Find existing inventory record for product/store combination.
    
    Args:
        db: Database session
        product_id: Product ID
        store_id: Store ID
    
    Returns:
        InventoryStore object if found, None otherwise
    """
    return db.query(InventoryStore).filter(
        InventoryStore.product_id == product_id,
        InventoryStore.store_id == store_id
    ).first()


def create_inventory_record(
    db: Session,
    product_id: int,
    store_id: int,
    record: InventoryRecord
) -> InventoryStore:
    """Create a new inventory record.
    
    Args:
        db: Database session
        product_id: Product ID
        store_id: Store ID
        record: Inventory record data
    
    Returns:
        Created InventoryStore object
    """
    from datetime import datetime
    from shared.utils import parse_date
    
    last_restock = None
    if record.last_restock_date:
        last_restock = parse_date(record.last_restock_date)
    
    inventory = InventoryStore(
        product_id=product_id,
        store_id=store_id,
        quantity_in_stock=record.quantity_in_stock,
        quantity_reserved=record.quantity_reserved,
        last_restock_date=last_restock,
        minimum_stock=record.minimum_stock,
        maximum_stock=record.maximum_stock,
        reorder_point=record.reorder_point,
    )
    
    db.add(inventory)
    db.commit()
    db.refresh(inventory)
    
    return inventory


def update_inventory_record(
    db: Session,
    inventory: InventoryStore,
    record: InventoryRecord
) -> InventoryStore:
    """Update an existing inventory record.
    
    Args:
        db: Database session
        inventory: Existing inventory record to update
        record: New inventory data
    
    Returns:
        Updated InventoryStore object
    """
    from datetime import datetime
    from shared.utils import parse_date
    
    inventory.quantity_in_stock = record.quantity_in_stock
    inventory.quantity_reserved = record.quantity_reserved
    
    if record.last_restock_date:
        inventory.last_restock_date = parse_date(record.last_restock_date)
    
    inventory.minimum_stock = record.minimum_stock
    inventory.maximum_stock = record.maximum_stock
    inventory.reorder_point = record.reorder_point
    inventory.last_updated = datetime.utcnow()
    
    db.commit()
    db.refresh(inventory)
    
    return inventory


@router.post("/inventory", response_model=InventoryIngestResponse, status_code=status.HTTP_201_CREATED)
def ingest_inventory(
    request: InventoryIngestRequest,
    db: Session = Depends(get_db)
):
    """Ingest inventory data into the system.
    
    This endpoint accepts a list of inventory records and creates or updates
    inventory entries in the database. It handles duplicate entries by updating
    existing records rather than creating duplicates.
    
    Args:
        request: Inventory ingestion request containing records
        db: Database session
    
    Returns:
        InventoryIngestResponse with status and counts
    
    Raises:
        HTTPException 400: If request payload is empty
        HTTPException 422: If validation fails for required fields
    """
    # Handle empty payload
    if not request.records:
        raise HTTPException(
            status_code=HTTP_STATUS["BAD_REQUEST"],
            detail=ERROR_MESSAGES["INVALID_FORMAT"]
        )
    
    records_created = 0
    records_updated = 0
    duplicates_handled = False
    errors: List[str] = []
    
    for record in request.records:
        try:
            # Validate required fields are present and non-negative
            if record.quantity_in_stock < 0:
                raise HTTPException(
                    status_code=HTTP_STATUS["UNPROCESSABLE_ENTITY"],
                    detail="quantity_in_stock cannot be negative"
                )
            
            # Get or verify product exists
            product = get_or_create_product(db, record.product_sku)
            if not product:
                errors.append(f"Product with SKU '{record.product_sku}' not found")
                continue
            
            # Get or verify store exists
            store = get_or_create_store(db, record.store_code)
            if not store:
                errors.append(f"Store with code '{record.store_code}' not found")
                continue
            
            # Check for existing inventory record
            existing_inventory = find_existing_inventory(db, product.id, store.id)
            
            if existing_inventory:
                # Update existing record (handle duplicate)
                update_inventory_record(db, existing_inventory, record)
                records_updated += 1
                duplicates_handled = True
            else:
                # Create new record
                create_inventory_record(db, product.id, store.id, record)
                records_created += 1
                
        except HTTPException:
            raise
        except IntegrityError as e:
            # Handle race condition - try to update instead
            db.rollback()
            try:
                product = get_or_create_product(db, record.product_sku)
                store = get_or_create_store(db, record.store_code)
                existing = find_existing_inventory(db, product.id, store.id)
                if existing:
                    update_inventory_record(db, existing, record)
                    records_updated += 1
                    duplicates_handled = True
            except Exception as inner_e:
                logger.error(f"Error handling duplicate: {inner_e}")
                errors.append(f"Error processing SKU {record.product_sku}: {str(inner_e)}")
        except Exception as e:
            logger.error(f"Error ingesting inventory record: {e}")
            errors.append(f"Error processing SKU {record.product_sku}: {str(e)}")
    
    return InventoryIngestResponse(
        status="success" if records_created > 0 or records_updated > 0 else "error",
        records_created=records_created,
        records_updated=records_updated,
        duplicates_handled=duplicates_handled,
        errors=errors
    )


@router.get("/inventory/health")
def inventory_ingestion_health():
    """Health check for inventory ingestion service.
    
    Returns:
        Dictionary with health status
    """
    return {
        "status": "healthy",
        "service": "inventory_ingestion",
        "version": "1.0.0"
    }


def validate_inventory_payload(payload: Dict[str, Any]) -> List[str]:
    """Validate inventory payload and return list of errors.
    
    Args:
        payload: Raw inventory payload to validate
    
    Returns:
        List of validation error messages
    """
    errors: List[str] = []
    
    if not payload:
        errors.append("Empty payload provided")
        return errors
    
    if "records" not in payload:
        errors.append("Missing required field: records")
        return errors
    
    records = payload.get("records", [])
    if not records:
        errors.append("Empty records list provided")
        return errors
    
    for idx, record in enumerate(records):
        if "product_sku" not in record:
            errors.append(f"Record {idx}: Missing required field 'product_sku'")
        
        if "store_code" not in record:
            errors.append(f"Record {idx}: Missing required field 'store_code'")
        
        if "quantity_in_stock" not in record:
            errors.append(f"Record {idx}: Missing required field 'quantity_in_stock'")
        elif record.get("quantity_in_stock", 0) < 0:
            errors.append(f"Record {idx}: Negative quantity_in_stock not allowed")
    
    return errors


# Import required for Index creation in InventoryStore model
from sqlalchemy import Index

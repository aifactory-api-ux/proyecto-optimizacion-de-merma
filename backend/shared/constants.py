"""
Shared constants for the application.

This module contains all application-wide constants including
default values, error messages, status codes, and configuration constants.
"""

from enum import Enum
from typing import Dict, Final


# API Configuration
API_VERSION: Final[str] = "1.0.0"
API_TITLE: Final[str] = "Merma Optimization API"
API_DESCRIPTION: Final[str] = "API for optimizing waste management in perishable products"

# Application Configuration
APP_NAME: Final[str] = "merma-optimization"
APP_ENV_DEFAULT: Final[str] = "development"

# Date/Time Formats
ISO8601_FORMAT: Final[str] = "%Y-%m-%dT%H:%M:%S.%fZ"
DATE_FORMAT: Final[str] = "%Y-%m-%d"
DATETIME_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"

# Pagination Defaults
DEFAULT_PAGE_SIZE: Final[int] = 20
MAX_PAGE_SIZE: Final[int] = 100
MIN_PAGE_SIZE: Final[int] = 1

# Cache Configuration
CACHE_TTL_SHORT: Final[int] = 300  # 5 minutes
CACHE_TTL_MEDIUM: Final[int] = 1800  # 30 minutes
CACHE_TTL_LONG: Final[int] = 3600  # 1 hour
CACHE_TTL_DAILY: Final[int] = 86400  # 24 hours

# Request Configuration
REQUEST_TIMEOUT_DEFAULT: Final[int] = 30
REQUEST_TIMEOUT_LONG: Final[int] = 60
MAX_REQUEST_SIZE: Final[int] = 10485760  # 10MB

# JWT Configuration
JWT_ALGORITHM: Final[str] = "HS256"
JWT_EXPIRATION_MINUTES: Final[int] = 60 * 24  # 24 hours

# Alert Severity Levels
class AlertSeverity(str, Enum):
    """Enum for alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


# Waste Calculation Constants
WASTE_COST_MULTIPLIER: Final[float] = 1.0
DEFAULT_WASTE_THRESHOLD: Final[float] = 0.05  # 5%
CRITICAL_WASTE_THRESHOLD: Final[float] = 0.15  # 15%

# Demand Prediction Constants
FORECAST_WINDOW_DAYS: Final[int] = 7
FORECAST_HISTORY_DAYS: Final[int] = 30
MIN_HISTORY_FOR_PREDICTION: Final[int] = 14

# Database Configuration
DB_POOL_SIZE: Final[int] = 5
DB_MAX_OVERFLOW: Final[int] = 10
DB_POOL_TIMEOUT: Final[int] = 30

# AWS Configuration
S3_DEFAULT_BUCKET: Final[str] = "merma-data"
S3_REGION_DEFAULT: Final[str] = "us-east-1"

# Error Messages
ERROR_MESSAGES: Dict[str, str] = {
    "INVALID_CREDENTIALS": "Invalid username or password",
    "TOKEN_EXPIRED": "The authentication token has expired",
    "TOKEN_INVALID": "The authentication token is invalid",
    "UNAUTHORIZED": "Unauthorized access",
    "FORBIDDEN": "Access forbidden",
    "NOT_FOUND": "Resource not found",
    "VALIDATION_ERROR": "Validation error in request data",
    "INTERNAL_ERROR": "Internal server error",
    "SERVICE_UNAVAILABLE": "Service temporarily unavailable",
    "DATABASE_ERROR": "Database operation failed",
    "CACHE_ERROR": "Cache operation failed",
    "EXTERNAL_SERVICE_ERROR": "External service integration failed",
    "INVALID_DATE_RANGE": "Invalid date range provided",
    "INVALID_PRODUCT": "Invalid product ID",
    "INVALID_STORE": "Invalid store ID",
    "MISSING_REQUIRED_FIELD": "Required field is missing",
    "INVALID_FORMAT": "Invalid format for field",
}

# HTTP Status Codes
HTTP_STATUS: Dict[str, int] = {
    "OK": 200,
    "CREATED": 201,
    "NO_CONTENT": 204,
    "BAD_REQUEST": 400,
    "UNAUTHORIZED": 401,
    "FORBIDDEN": 403,
    "NOT_FOUND": 404,
    "CONFLICT": 409,
    "UNPROCESSABLE_ENTITY": 422,
    "INTERNAL_ERROR": 500,
    "SERVICE_UNAVAILABLE": 503,
}

# Health Check Messages
HEALTH_MESSAGES: Dict[str, str] = {
    "HEALTHY": "Service is healthy",
    "DEGRADED": "Service is running with degraded performance",
    "UNHEALTHY": "Service is not healthy",
    "STARTING": "Service is starting",
}

# Waste Category Thresholds (percentage of inventory)
class WasteCategory(str, Enum):
    """Enum for waste categories based on severity."""
    LOW = "low"          # < 5%
    MODERATE = "moderate"  # 5-10%
    HIGH = "high"        # 10-20%
    CRITICAL = "critical" # > 20%



# Store Status
class StoreStatus(str, Enum):
    """Enum for store status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PILOT = "pilot"
    ARCHIVED = "archived"



# Product Categories (for perishable goods)
class ProductCategory(str, Enum):
    """Enum for product categories."""
    DAIRY = "dairy"
    BAKERY = "bakery"
    MEAT = "meat"
    PRODUCE = "produce"
    SEAFOOD = "seafood"
    FROZEN = "frozen"
    OTHER = "other"


# Recommendation Types
class RecommendationType(str, Enum):
    """Enum for recommendation types."""
    REORDER = "reorder"
    DISCOUNT = "discount"
    NO_REORDER = "no_reorder"
    MARKDOWN = "markdown"
    DONATE = "donate"
    DISPOSE = "dispose"


# Data Source Types
class DataSourceType(str, Enum):
    """Enum for data source types."""
    POS = "pos"
    INVENTORY = "inventory"
    ERP = "erp"
    MANUAL = "manual"
    FORECAST = "forecast"


# Validation Patterns
VALIDATION_PATTERNS: Dict[str, str] = {
    "EMAIL": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
    "USERNAME": r"^[a-zA-Z0-9_]{3,50}$",
    "PASSWORD": r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$",
    "PHONE": r"^\+?[1-9]\d{1,14}$",
    "SKU": r"^[A-Z0-9-]{3,20}$",
}


# Logging Configuration
LOG_FORMAT: Final[str] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"

# File Upload Configuration
ALLOWED_FILE_EXTENSIONS: tuple = (".csv", ".xlsx", ".xls", ".json")
MAX_FILE_SIZE: Final[int] = 52428800  # 50MB

# Metrics Calculation Intervals
METRICS_INTERVAL_HOURLY: Final[int] = 1
METRICS_INTERVAL_DAILY: Final[int] = 24
METRICS_INTERVAL_WEEKLY: Final[int] = 168
METRICS_INTERVAL_MONTHLY: Final[int] = 720

# Forecasting Configuration
FORECAST_CONFIDENCE_LEVEL: Final[float] = 0.95
FORECAST_MIN_CONFIDENCE: Final[float] = 0.70
FORECAST_SEASONAL_ADJUSTMENT: Final[float] = 1.1

# Business Rules
MIN_STOCK_THRESHOLD: Final[float] = 0.0
MAX_STOCK_WARNING: Final[float] = 1000.0
OPTIMAL_STOCK_RATIO: Final[float] = 0.85
DEMAND_VOLATILITY_THRESHOLD: Final[float] = 0.30

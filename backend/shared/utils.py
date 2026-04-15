"""
Shared Utilities

Common utility functions used across the backend application.
Provides helpers for data formatting, validation, and common operations.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
import json
import logging
import re

logger = logging.getLogger(__name__)


def format_date_iso(date: datetime) -> str:
    """Convert datetime to ISO 8601 string format.
    
    Args:
        date: datetime object to format
        
    Returns:
        ISO 8601 formatted date string
    """
    return date.isoformat()


def parse_date_iso(date_string: str) -> Optional[datetime]:
    """Parse ISO 8601 date string to datetime.
    
    Args:
        date_string: ISO 8601 formatted date string
        
    Returns:
        datetime object or None if parsing fails
    """
    try:
        return datetime.fromisoformat(date_string)
    except (ValueError, TypeError):
        return None


def calculate_date_range(
    start_date: Optional[datetime],
    end_date: Optional[datetime],
    default_days: int = 30
) -> tuple[datetime, datetime]:
    """Calculate date range with optional defaults.
    
    Args:
        start_date: Start date (optional)
        end_date: End date (optional)
        default_days: Default number of days for range
        
    Returns:
        Tuple of (start_date, end_date)
    """
    now = datetime.utcnow()
    if end_date is None:
        end_date = now
    if start_date is None:
        start_date = end_date - timedelta(days=default_days)
    return start_date, end_date


def sanitize_string(text: str, max_length: Optional[int] = None) -> str:
    """Sanitize string input by removing special characters.
    
    Args:
        text: Input string to sanitize
        max_length: Optional maximum length
        
    Returns:
        Sanitized string
    """
    sanitized = re.sub(r'[^\w\s\-_]', '', text)
    if max_length and len(sanitized) > max_length:
        return sanitized[:max_length]
    return sanitized.strip()


def safe_divide(
    numerator: Union[int, float],
    denominator: Union[int, float],
    default: float = 0.0
) -> float:
    """Safely divide two numbers, returning default if denominator is zero.
    
    Args:
        numerator: Numerator value
        denominator: Denominator value
        default: Default value to return if division fails
        
    Returns:
        Result of division or default value
    """
    try:
        if denominator == 0:
            return default
        return float(numerator) / float(denominator)
    except (TypeError, ValueError):
        return default


def calculate_percentage(
    part: Union[int, float],
    whole: Union[int, float],
    decimals: int = 2
) -> float:
    """Calculate percentage with optional decimal precision.
    
    Args:
        part: Portion value
        whole: Total value
        decimals: Number of decimal places
        
    Returns:
        Percentage value
    """
    result = safe_divide(part * 100, whole)
    return round(result, decimals)


def format_currency(amount: float, currency_symbol: str = "$") -> str:
    """Format amount as currency string.
    
    Args:
        amount: Numeric amount
        currency_symbol: Currency symbol to use
        
    Returns:
        Formatted currency string
    """
    return f"{currency_symbol}{amount:,.2f}"


def format_number(number: float, decimals: int = 2) -> str:
    """Format number with specified decimal places.
    
    Args:
        number: Numeric value
        decimals: Number of decimal places
        
    Returns:
        Formatted number string
    """
    return f"{number:,.{decimals}f}"


def paginate_list(
    items: List[Any],
    page: int = 1,
    page_size: int = 20
) -> Dict[str, Any]:
    """Paginate a list of items.
    
    Args:
        items: List of items to paginate
        page: Current page number
        page_size: Number of items per page
        
    Returns:
        Dictionary with paginated results and metadata
    """
    total = len(items)
    total_pages = (total + page_size - 1) // page_size
    start = (page - 1) * page_size
    end = start + page_size
    
    return {
        "items": items[start:end],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }


def serialize_json(data: Any) -> str:
    """Serialize data to JSON string.
    
    Args:
        data: Data to serialize
        
    Returns:
        JSON string representation
    """
    return json.dumps(data, default=str)


def deserialize_json(json_string: str) -> Optional[Any]:
    """Deserialize JSON string to Python object.
    
    Args:
        json_string: JSON string to deserialize
        
    Returns:
        Deserialized Python object or None
    """
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return None


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate string to maximum length.
    
    Args:
        text: Input string
        max_length: Maximum length
        suffix: Suffix to append if truncated
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def is_valid_email(email: str) -> bool:
    """Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid email format
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_valid_date_range(start: datetime, end: datetime) -> bool:
    """Check if date range is valid.
    
    Args:
        start: Start date
        end: End date
        
    Returns:
        True if range is valid (start before end)
    """
    return start < end


def generate_slug(text: str) -> str:
    """Generate URL-friendly slug from text.
    
    Args:
        text: Input text
        
    Returns:
        URL-friendly slug
    """
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = text.strip('-')
    return text


def get_quarter_from_date(date: datetime) -> int:
    """Get quarter number (1-4) from datetime.
    
    Args:
        date: datetime object
        
    Returns:
        Quarter number (1-4)
    """
    return (date.month - 1) // 3 + 1


def get_week_number(date: datetime) -> int:
    """Get ISO week number from datetime.
    
    Args:
        date: datetime object
        
    Returns:
        ISO week number
    """
    return date.isocalendar()[1]


def convert_to_float(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float.
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        Float value or default
    """
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def convert_to_int(value: Any, default: int = 0) -> int:
    """Safely convert value to integer.
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        Integer value or default
    """
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """Flatten nested dictionary.
    
    Args:
        d: Dictionary to flatten
        parent_key: Parent key for recursion
        sep: Separator for keys
        
    Returns:
        Flattened dictionary
    """
    items: List[tuple[str, Any]] = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def deep_merge(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries.
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary (takes precedence)
        
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def filter_none_values(d: Dict[str, Any]) -> Dict[str, Any]:
    """Filter out None values from dictionary.
    
    Args:
        d: Dictionary to filter
        
    Returns:
        Dictionary with None values removed
    """
    return {k: v for k, v in d.items() if v is not None}


def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split list into chunks.
    
    Args:
        items: List to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def remove_duplicates(items: List[Any], key: Optional[str] = None) -> List[Any]:
    """Remove duplicates from list while preserving order.
    
    Args:
        items: List to deduplicate
        key: Optional key function for comparison
        
    Returns:
        Deduplicated list
    """
    if key is None:
        seen = set()
        result = []
        for item in items:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result
    else:
        seen = set()
        result = []
        for item in items:
            k = key(item)
            if k not in seen:
                seen.add(k)
                result.append(item)
        return result

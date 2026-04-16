"""
Shared Utilities

Common utility functions used across the backend application.
Provides helpers for data formatting, validation, and common operations.
"""

from datetime import datetime, timedelta, timezone
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
    now = datetime.now(timezone.utc)
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


def add_days(date: datetime, days: int) -> datetime:
    """Add days to a datetime.
    
    Args:
        date: datetime object
        days: Number of days to add (can be negative)
    
    Returns:
        New datetime with days added
    """
    return date + timedelta(days=days)


def add_hours(date: datetime, hours: int) -> datetime:
    """Add hours to a datetime.
    
    Args:
        date: datetime object
        hours: Number of hours to add (can be negative)
    
    Returns:
        New datetime with hours added
    """
    return date + timedelta(hours=hours)


def get_current_date() -> datetime:
    """Get current date.
    
    Returns:
        Current datetime (date only)
    """
    return datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)


def get_current_datetime() -> datetime:
    """Get current datetime.
    
    Returns:
        Current datetime
    """
    return datetime.now(timezone.utc)


def format_date(date: datetime, fmt: str = "%Y-%m-%d") -> str:
    """Format date as string.
    
    Args:
        date: datetime object
        fmt: Format string
    
    Returns:
        Formatted date string
    """
    return date.strftime(fmt)


def format_datetime(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime as string.
    
    Args:
        dt: datetime object
        fmt: Format string
    
    Returns:
        Formatted datetime string
    """
    return dt.strftime(fmt)


def parse_date(date_string: str, fmt: str = "%Y-%m-%d") -> Optional[datetime]:
    """Parse date string to datetime.
    
    Args:
        date_string: Date string to parse
        fmt: Format string
    
    Returns:
        datetime object or None if parsing fails
    """
    try:
        return datetime.strptime(date_string, fmt)
    except (ValueError, TypeError):
        return None


def to_iso8601(dt: datetime) -> str:
    """Convert datetime to ISO 8601 string.
    
    Args:
        dt: datetime object
    
    Returns:
        ISO 8601 formatted string
    """
    return dt.isoformat()


def to_json(data: Any) -> str:
    """Serialize data to JSON string.
    
    Args:
        data: Data to serialize
    
    Returns:
        JSON string
    """
    return json.dumps(data, default=str)


def parse_json(json_string: str) -> Optional[Any]:
    """Parse JSON string.
    
    Args:
        json_string: JSON string to parse
    
    Returns:
        Parsed data or None
    """
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return None


def date_range(start: datetime, end: datetime, step: timedelta = timedelta(days=1)) -> List[datetime]:
    """Generate date range.
    
    Args:
        start: Start datetime
        end: End datetime
        step: Step size
    
    Returns:
        List of datetimes in range
    """
    result = []
    current = start
    while current <= end:
        result.append(current)
        current += step
    return result


def round_decimal(value: float, decimals: int = 2) -> float:
    """Round decimal value.
    
    Args:
        value: Value to round
        decimals: Number of decimal places
    
    Returns:
        Rounded value
    """
    return round(value, decimals)


def calculate_moving_average(values: List[float], window: int = 7) -> List[float]:
    """Calculate moving average.
    
    Args:
        values: List of values
        window: Window size
    
    Returns:
        List of moving averages
    """
    if len(values) < window:
        return values
    result = []
    for i in range(len(values) - window + 1):
        window_values = values[i:i + window]
        result.append(sum(window_values) / window)
    return result


def calculate_growth_rate(current: float, previous: float) -> float:
    """Calculate growth rate.
    
    Args:
        current: Current value
        previous: Previous value
    
    Returns:
        Growth rate as percentage
    """
    if previous == 0:
        return 0.0
    return ((current - previous) / previous) * 100


def convert_to_bool(value: Any) -> bool:
    """Convert value to boolean.
    
    Args:
        value: Value to convert
    
    Returns:
        Boolean value
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "1", "yes", "on")
    return bool(value)


def camel_to_snake(text: str) -> str:
    """Convert camelCase to snake_case.
    
    Args:
        text: Text in camelCase
    
    Returns:
        Text in snake_case
    """
    return re.sub(r'(?<!^)(?=[A-Z])', '_', text).lower()


def snake_to_camel(text: str) -> str:
    """Convert snake_case to camelCase.
    
    Args:
        text: Text in snake_case
    
    Returns:
        Text in camelCase
    """
    components = text.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def filter_dict(d: Dict[str, Any], include_keys: Optional[List[str]] = None, exclude_keys: Optional[List[str]] = None) -> Dict[str, Any]:
    """Filter dictionary by keys.
    
    Args:
        d: Dictionary to filter
        include_keys: Keys to include
        exclude_keys: Keys to exclude
    
    Returns:
        Filtered dictionary
    """
    if include_keys:
        return {k: v for k, v in d.items() if k in include_keys}
    if exclude_keys:
        return {k: v for k, v in d.items() if k not in exclude_keys}
    return d


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Merge two dictionaries.
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary (takes precedence)
    
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    result.update(dict2)
    return result


def get_nested_value(d: Dict[str, Any], path: str, default: Any = None) -> Any:
    """Get nested value from dictionary.
    
    Args:
        d: Dictionary
        path: Dot-separated path (e.g., "a.b.c")
        default: Default value if not found
    
    Returns:
        Nested value or default
    """
    keys = path.split('.')
    value = d
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
        else:
            return default
        if value is None:
            return default
    return value


def set_nested_value(d: Dict[str, Any], path: str, value: Any) -> Dict[str, Any]:
    """Set nested value in dictionary.
    
    Args:
        d: Dictionary
        path: Dot-separated path
        value: Value to set
    
    Returns:
        Updated dictionary
    """
    keys = path.split('.')
    current = d
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    current[keys[-1]] = value
    return d


def deduplicate_list(items: List[Any]) -> List[Any]:
    """Remove duplicates from list.
    
    Args:
        items: List to deduplicate
    
    Returns:
        Deduplicated list
    """
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def validate_email(email: str) -> bool:
    """Validate email format.
    
    Args:
        email: Email to validate
    
    Returns:
        True if valid
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password: str) -> bool:
    """Validate password strength.
    
    Args:
        password: Password to validate
    
    Returns:
        True if valid (min 8 chars)
    """
    return len(password) >= 8


def validate_username(username: str) -> bool:
    """Validate username format.
    
    Args:
        username: Username to validate
    
    Returns:
        True if valid (alphanumeric and underscore)
    """
    pattern = r'^[a-zA-Z0-9_]{3,30}$'
    return bool(re.match(pattern, username))


def generate_uuid() -> str:
    """Generate UUID.
    
    Returns:
        UUID string
    """
    import uuid
    return str(uuid.uuid4())


def generate_hash(data: str) -> str:
    """Generate hash of data.
    
    Args:
        data: Data to hash
    
    Returns:
        Hash string
    """
    import hashlib
    return hashlib.sha256(data.encode()).hexdigest()


def verify_hash(data: str, hash: str) -> bool:
    """Verify hash.
    
    Args:
        data: Data to verify
        hash: Expected hash
    
    Returns:
        True if valid
    """
    import hashlib
    return hashlib.sha256(data.encode()).hexdigest() == hash


def generate_api_key() -> str:
    """Generate API key.
    
    Returns:
        API key string
    """
    import secrets
    return secrets.token_urlsafe(32)


def is_valid_uuid(value: str) -> bool:
    """Check if valid UUID.
    
    Args:
        value: Value to check
    
    Returns:
        True if valid UUID
    """
    import uuid
    try:
        uuid.UUID(value)
        return True
    except (ValueError, AttributeError):
        return False


def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """Mask sensitive data.
    
    Args:
        data: Data to mask
        visible_chars: Number of visible characters
    
    Returns:
        Masked data
    """
    if len(data) <= visible_chars:
        return "*" * len(data)
    return data[:visible_chars] + "*" * (len(data) - visible_chars)

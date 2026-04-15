"""AWS Module

This package provides AWS service integrations for the waste optimization system.
"""

from app.aws.s3 import (
    S3Manager,
    get_s3_manager,
    init_s3_manager,
    upload_historical_data,
    list_historical_data,
)

__all__ = [
    "S3Manager",
    "get_s3_manager",
    "init_s3_manager",
    "upload_historical_data",
    "list_historical_data",
]

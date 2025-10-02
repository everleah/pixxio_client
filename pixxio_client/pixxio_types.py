"""Custom type definitions for the PIXXIO Client library.

This module defines common types used across the PIXXIO API client based on
the OpenAPI specification patterns.
"""

from typing import Dict, List, Optional, Union, Any, TypeVar, IO, BinaryIO, TextIO, Callable, Awaitable
from types import SimpleNamespace
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

# Basic PIXXIO types based on OpenAPI schema analysis
PIXXIOId = int  # "An ID is a number" - integer type with minimum 0
PIXXIODateTime = str  # "A date and datetime in the format of YYYY-MM-DD HH:MM:SS"
PIXXIOTerm = str  # "a string term" - general string identifier
PIXXIOToken = str  # "A token" - API key or authentication token

# Response data structures
ResponseData = Union[Dict[str, Any], List[Dict[str, Any]], SimpleNamespace, None]
JSONDict = Dict[str, Any]
QueryParams = Dict[str, Union[str, int, bool, List[str]]]

# File and upload related types
FileHandle = Union[IO[bytes], BinaryIO, TextIO, Any]  # File-like object for uploads
FileParams = Optional[Dict[str, FileHandle]]  # Files parameter for requests library

# Common API parameters
ResponseFields = List[str]  # Fields to include in API responses
FilterParams = Dict[str, Any]  # Filtering parameters for API calls

# Generic type for API resources (will be bound to actual ResourceBase later)
T = TypeVar('T')

# HTTP method types
HTTPMethod = str  # 'GET', 'POST', 'PUT', 'DELETE', etc.

# Common API response structure patterns
class PIXXIOResponse:
    """Base response structure from PIXXIO API."""
    
    def __init__(self, data: ResponseData = None, success: bool = True):
        self.data = data
        self.success = success

# Exception types for better error handling
PIXXIOError = Exception  # Base exception type for PIXXIO-specific errors

# Authentication types
APIKey = str  # PIXXIO API key string
AuthHeaders = Dict[str, str]  # HTTP headers for authentication

# Async job support types

class JobStatus(Enum):
    """PIXXIO job status enumeration."""
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"

@dataclass
class JobInfo:
    """Information about a PIXXIO job."""
    id: PIXXIOId
    status: JobStatus
    progress: Optional[int] = None  # 0-100 percentage
    message: Optional[str] = None
    created_date: Optional[PIXXIODateTime] = None
    completed_date: Optional[PIXXIODateTime] = None
    result_data: Optional[ResponseData] = None

# Job tracking callback types
JobCallback = Callable[[JobInfo], None]
AsyncJobCallback = Callable[[JobInfo], Awaitable[None]]
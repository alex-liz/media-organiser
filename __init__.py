"""
Media Organiser - A tool for organizing and deduplicating media files.
"""

__version__ = "2.0.0"
__author__ = "alex-liz"

from .core.organiser import MediaOrganiser
from .core.duplicate_detector import DuplicateDetector
from .core.date_extractor import DateExtractor
from .utils.exceptions import (
    MediaOrganiserError,
    FileOperationError,
    DateExtractionError,
    DuplicateDetectionError
)

__all__ = [
    'MediaOrganiser',
    'DuplicateDetector',
    'DateExtractor',
    'MediaOrganiserError',
    'FileOperationError',
    'DateExtractionError',
    'DuplicateDetectionError'
]

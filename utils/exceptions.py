"""
Custom exceptions for the media organiser.
"""


class MediaOrganiserError(Exception):
    """Base exception for all media organiser errors."""
    pass


class FileOperationError(MediaOrganiserError):
    """Exception raised for file operation errors."""
    pass


class DateExtractionError(MediaOrganiserError):
    """Exception raised when date extraction fails."""
    pass


class DuplicateDetectionError(MediaOrganiserError):
    """Exception raised during duplicate detection."""
    pass


class InvalidPathError(MediaOrganiserError):
    """Exception raised for invalid paths."""
    pass


class PermissionError(MediaOrganiserError):
    """Exception raised for permission issues."""
    pass

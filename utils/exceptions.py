"""
Custom exceptions for the media organiser.
"""


class MediaOrganizerError(Exception):
    """Base exception for all media organiser errors."""
    pass


class FileOperationError(MediaOrganizerError):
    """Exception raised for file operation errors."""
    pass


class DateExtractionError(MediaOrganizerError):
    """Exception raised when date extraction fails."""
    pass


class DuplicateDetectionError(MediaOrganizerError):
    """Exception raised during duplicate detection."""
    pass


class InvalidPathError(MediaOrganizerError):
    """Exception raised for invalid paths."""
    pass


class PermissionError(MediaOrganizerError):
    """Exception raised for permission issues."""
    pass

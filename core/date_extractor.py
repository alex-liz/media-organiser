"""
Date extraction from media files.
"""

import re
from pathlib import Path
from datetime import datetime
from typing import Optional
from ..utils.exceptions import DateExtractionError
from ..utils.logger import get_logger

logger = get_logger(__name__)

try:
    from PIL import Image
    from PIL.ExifTags import TAGS

    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    logger.warning("Pillow not available. EXIF data reading will be disabled.")


class DateExtractor:
    """Extract dates from media files using multiple methods."""

    # Date patterns in filenames
    DATE_PATTERNS = [
        # YYYY-MM-DD or YYYY_MM_DD
        (r'(\d{4})[-_](\d{2})[-_](\d{2})', '%Y-%m-%d'),
        # YYYYMMDD
        (r'(\d{4})(\d{2})(\d{2})', '%Y%m%d'),
        # DD-MM-YYYY or DD_MM_YYYY
        (r'(\d{2})[-_](\d{2})[-_](\d{4})', '%d-%m-%Y'),
        # IMG_YYYYMMDD
        (r'IMG[_-](\d{4})(\d{2})(\d{2})', '%Y%m%d'),
        # VID_YYYYMMDD
        (r'VID[_-](\d{4})(\d{2})(\d{2})', '%Y%m%d'),
    ]

    def __init__(self):
        """Initialize the date extractor."""
        self.stats = {
            'exif': 0,
            'filename': 0,
            'modified': 0,
            'failed': 0
        }

    def extract_date(self, file_path: Path) -> Optional[datetime]:
        """
        Extract date from a media file.

        Args:
            file_path: Path to the media file

        Returns:
            Datetime object or None if extraction fails
        """
        try:
            # Try EXIF first for images
            if PILLOW_AVAILABLE and self._is_image(file_path):
                date = self._extract_from_exif(file_path)
                if date:
                    self.stats['exif'] += 1
                    return date

            # Try filename patterns
            date = self._extract_from_filename(file_path)
            if date:
                self.stats['filename'] += 1
                return date

            # Fallback to file modification time
            date = self._extract_from_modification_time(file_path)
            if date:
                self.stats['modified'] += 1
                return date

            self.stats['failed'] += 1
            logger.warning(f"Could not extract date from: {file_path}")
            return None

        except Exception as e:
            self.stats['failed'] += 1
            logger.error(f"Error extracting date from {file_path}: {str(e)}")
            return None

    def _is_image(self, file_path: Path) -> bool:
        """Check if file is an image."""
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.heic'}
        return file_path.suffix.lower() in image_extensions

    def _extract_from_exif(self, file_path: Path) -> Optional[datetime]:
        """
        Extract date from EXIF data.

        Args:
            file_path: Path to the image file

        Returns:
            Datetime object or None
        """
        try:
            image = Image.open(file_path)
            exif_data = image._getexif()

            if not exif_data:
                return None

            # Look for DateTimeOriginal (36867) or DateTime (306)
            for tag_id in [36867, 306]:
                if tag_id in exif_data:
                    date_str = exif_data[tag_id]
                    # EXIF date format: "YYYY:MM:DD HH:MM:SS"
                    date = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                    logger.debug(f"Extracted EXIF date from {file_path}: {date}")
                    return date

            return None

        except Exception as e:
            logger.debug(f"Failed to extract EXIF from {file_path}: {str(e)}")
            return None

    def _extract_from_filename(self, file_path: Path) -> Optional[datetime]:
        """
        Extract date from filename patterns.

        Args:
            file_path: Path to the file

        Returns:
            Datetime object or None
        """
        filename = file_path.stem

        for pattern, date_format in self.DATE_PATTERNS:
            match = re.search(pattern, filename)
            if match:
                try:
                    date_str = '-'.join(match.groups())
                    date = datetime.strptime(date_str, date_format)
                    logger.debug(f"Extracted date from filename {file_path}: {date}")
                    return date
                except ValueError:
                    continue

        return None

    def _extract_from_modification_time(self, file_path: Path) -> Optional[datetime]:
        """
        Extract date from file modification time.

        Args:
            file_path: Path to the file

        Returns:
            Datetime object or None
        """
        try:
            mtime = file_path.stat().st_mtime
            date = datetime.fromtimestamp(mtime)
            logger.debug(f"Using modification time for {file_path}: {date}")
            return date
        except Exception as e:
            logger.error(f"Failed to get modification time for {file_path}: {str(e)}")
            return None

    def get_stats(self) -> dict:
        """Get extraction statistics."""
        return self.stats.copy()

    def reset_stats(self):
        """Reset extraction statistics."""
        self.stats = {
            'exif': 0,
            'filename': 0,
            'modified': 0,
            'failed': 0
        }

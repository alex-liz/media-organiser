"""
Tests for date extraction.
"""

import pytest
from pathlib import Path
from datetime import datetime
from media_organiser.core.date_extractor import DateExtractor


class TestDateExtractor:

    def test_extract_from_filename_yyyymmdd(self, temp_dir):
        """Test date extraction from YYYYMMDD format."""
        file_path = temp_dir / "IMG_20240315_123456.jpg"
        file_path.write_bytes(b"test")

        extractor = DateExtractor()
        date = extractor.extract_date(file_path)

        assert date is not None
        assert date.year == 2024
        assert date.month == 3
        assert date.day == 15

    def test_extract_from_filename_with_separators(self, temp_dir):
        """Test date extraction with separators."""
        file_path = temp_dir / "photo_2024-03-15.jpg"
        file_path.write_bytes(b"test")

        extractor = DateExtractor()
        date = extractor.extract_date(file_path)

        assert date is not None
        assert date.year == 2024
        assert date.month == 3
        assert date.day == 15

    def test_extract_from_modification_time(self, temp_dir):
        """Test fallback to modification time."""
        file_path = temp_dir / "no_date_in_name.jpg"
        file_path.write_bytes(b"test")

        extractor = DateExtractor()
        date = extractor.extract_date(file_path)

        assert date is not None
        assert isinstance(date, datetime)

    def test_get_stats(self, temp_dir):
        """Test statistics tracking."""
        file_path = temp_dir / "IMG_20240315.jpg"
        file_path.write_bytes(b"test")

        extractor = DateExtractor()
        extractor.extract_date(file_path)

        stats = extractor.get_stats()

        assert 'filename' in stats
        assert stats['filename'] >= 1
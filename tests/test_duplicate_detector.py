"""
Tests for duplicate detection.
"""

import pytest
from media_organiser.core.duplicate_detector import DuplicateDetector


class TestDuplicateDetector:

    def test_scan_files(self, sample_images):
        """Test file scanning."""
        detector = DuplicateDetector()
        hash_map = detector.scan_files(sample_images)

        assert len(hash_map) == len(sample_images)

    def test_find_duplicates(self, duplicate_files):
        """Test duplicate detection."""
        detector = DuplicateDetector()
        detector.scan_files(duplicate_files)
        duplicates = detector.find_duplicates()

        assert len(duplicates) == 2  # 2 duplicates of the original

    def test_no_duplicates(self, sample_images):
        """Test with no duplicates."""
        detector = DuplicateDetector()
        detector.scan_files(sample_images)
        duplicates = detector.find_duplicates()

        assert len(duplicates) == 0

    def test_get_statistics(self, duplicate_files):
        """Test statistics generation."""
        detector = DuplicateDetector()
        detector.scan_files(duplicate_files)
        detector.find_duplicates()

        stats = detector.get_statistics()

        assert stats['total_files'] == 3
        assert stats['unique_files'] == 1
        assert stats['duplicate_count'] == 2

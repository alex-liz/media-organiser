"""
Tests for media organizer.
"""

import pytest
from media_organiser.core.organizer import MediaOrganizer, OrganizeMode


class TestMediaOrganizer:

    def test_initialization(self, temp_dir):
        """Test organizer initialization."""
        organizer = MediaOrganizer(
            temp_dir,
            organize_mode=OrganizeMode.YEAR_MONTH,
            remove_duplicates=True,
            dry_run=True
        )

        assert organizer.root_path == temp_dir
        assert organizer.organize_mode == OrganizeMode.YEAR_MONTH
        assert organizer.dry_run is True

    def test_dry_run_no_changes(self, sample_images):
        """Test that dry run doesn't modify files."""
        temp_dir = sample_images[0].parent

        organizer = MediaOrganizer(
            temp_dir,
            organize_mode=OrganizeMode.YEAR,
            dry_run=True
        )

        stats = organizer.process()

        # Files should still be in original location
        for img in sample_images:
            assert img.exists()

    def test_duplicate_removal(self, duplicate_files):
        """Test duplicate removal."""
        temp_dir = duplicate_files[0].parent

        organizer = MediaOrganizer(
            temp_dir,
            remove_duplicates=True,
            dry_run=False
        )

        stats = organizer.process()

        assert stats['duplicates_found'] == 2
        assert stats['duplicates_removed'] == 2

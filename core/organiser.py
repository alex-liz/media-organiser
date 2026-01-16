"""
Main media organizer class.
"""

from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum
from ..utils.file_operations import (
    safe_move_file,
    safe_delete_file,
    remove_empty_directories,
    scan_media_files,
    get_file_size_readable
)
from ..utils.exceptions import FileOperationError
from ..utils.logger import get_logger
from .date_extractor import DateExtractor
from .duplicate_detector import DuplicateDetector

logger = get_logger(__name__)


class OrganizeMode(Enum):
    """Organization modes."""
    NONE = "none"
    YEAR = "year"
    YEAR_MONTH = "year_month"
    YEAR_MONTH_DAY = "year_month_day"


class MediaOrganiser:
    """Main class for organizing media files."""

    def __init__(
            self,
            root_path: Path,
            organize_mode: OrganizeMode = OrganizeMode.NONE,
            remove_duplicates: bool = False,
            dry_run: bool = False
    ):
        """
        Initialize the media organizer.

        Args:
            root_path: Root directory to organize
            organize_mode: How to organize files
            remove_duplicates: Whether to remove duplicates
            dry_run: If True, don't make actual changes
        """
        self.root_path = Path(root_path)
        self.organize_mode = organize_mode
        self.remove_duplicates = remove_duplicates
        self.dry_run = dry_run

        self.date_extractor = DateExtractor()
        self.duplicate_detector = DuplicateDetector()

        self.stats = {
            'total_files': 0,
            'duplicates_found': 0,
            'duplicates_removed': 0,
            'files_organized': 0,
            'empty_folders_removed': 0,
            'space_freed': 0,
            'errors': 0
        }

    def process(self) -> Dict:
        """
        Process all media files in the root directory.

        Returns:
            Statistics dictionary
        """
        try:
            logger.info(f"Starting media organization for: {self.root_path}")
            logger.info(f"Organize mode: {self.organize_mode.value}")
            logger.info(f"Remove duplicates: {self.remove_duplicates}")
            logger.info(f"Dry run: {self.dry_run}")

            # Scan for media files
            media_files = scan_media_files(self.root_path)
            self.stats['total_files'] = len(media_files)

            if not media_files:
                logger.warning("No media files found")
                return self.stats

            # Process duplicates if requested
            if self.remove_duplicates:
                self._process_duplicates(media_files)
                # Update file list after duplicate removal
                media_files = [f for f in media_files if f.exists()]

            # Organize files if requested
            if self.organize_mode != OrganizeMode.NONE:
                self._organize_files(media_files)

            # Clean up empty directories
            if not self.dry_run:
                empty_count = remove_empty_directories(self.root_path)
                self.stats['empty_folders_removed'] = empty_count
                logger.info(f"Removed {empty_count} empty directories")

            self._print_summary()
            return self.stats

        except Exception as e:
            logger.error(f"Error during processing: {str(e)}")
            raise

    def _process_duplicates(self, files: List[Path]):
        """Process duplicate files."""
        logger.info("Scanning for duplicates...")

        try:
            self.duplicate_detector.scan_files(files)
            duplicates = self.duplicate_detector.find_duplicates()

            self.stats['duplicates_found'] = len(duplicates)

            if not duplicates:
                logger.info("No duplicates found")
                return

            # Get statistics before removal
            dup_stats = self.duplicate_detector.get_statistics()

            logger.info(f"Found {len(duplicates)} duplicate files")
            logger.info(f"Space to free: {get_file_size_readable(dup_stats['space_to_free'])}")

            if self.dry_run:
                logger.info("[DRY RUN] Would remove the following duplicates:")
                for dup in duplicates[:10]:  # Show first 10
                    logger.info(f"  - {dup}")
                if len(duplicates) > 10:
                    logger.info(f"  ... and {len(duplicates) - 10} more")
                return

            # Remove duplicates
            removed_count = 0
            for dup_path in duplicates:
                try:
                    file_size = dup_path.stat().st_size
                    safe_delete_file(dup_path)
                    removed_count += 1
                    self.stats['space_freed'] += file_size
                    logger.info(f"Removed duplicate: {dup_path}")
                except FileOperationError as e:
                    logger.error(f"Failed to remove {dup_path}: {str(e)}")
                    self.stats['errors'] += 1

            self.stats['duplicates_removed'] = removed_count
            logger.info(f"Removed {removed_count} duplicates")

        except Exception as e:
            logger.error(f"Error processing duplicates: {str(e)}")
            self.stats['errors'] += 1

    def _organize_files(self, files: List[Path]):
        """Organize files by date."""
        logger.info(f"Organizing files by {self.organize_mode.value}...")

        organized_count = 0

        for file_path in files:
            try:
                # Extract date
                date = self.date_extractor.extract_date(file_path)

                if not date:
                    logger.warning(f"Could not extract date from: {file_path}")
                    continue

                # Generate destination path
                dest_dir = self._get_destination_directory(date)
                dest_path = dest_dir / file_path.name

                # Skip if already in correct location
                if file_path.parent == dest_dir:
                    continue

                if self.dry_run:
                    logger.info(f"[DRY RUN] Would move: {file_path} -> {dest_dir}")
                else:
                    safe_move_file(file_path, dest_path)
                    logger.info(f"Organized: {file_path.name} -> {dest_dir}")

                organized_count += 1

            except FileOperationError as e:
                logger.error(f"Failed to organize {file_path}: {str(e)}")
                self.stats['errors'] += 1
            except Exception as e:
                logger.error(f"Unexpected error organizing {file_path}: {str(e)}")
                self.stats['errors'] += 1

        self.stats['files_organized'] = organized_count
        logger.info(f"Organized {organized_count} files")

    def _get_destination_directory(self, date: datetime) -> Path:
        """
        Get destination directory based on organize mode.

        Args:
            date: File date

        Returns:
            Destination directory path
        """
        if self.organize_mode == OrganizeMode.YEAR:
            return self.root_path / f"{date.year}"

        elif self.organize_mode == OrganizeMode.YEAR_MONTH:
            return self.root_path / f"{date.year}" / f"{date.month:02d}"

        elif self.organize_mode == OrganizeMode.YEAR_MONTH_DAY:
            return self.root_path / f"{date.year}" / f"{date.month:02d}" / f"{date.day:02d}"

        return self.root_path

    def _print_summary(self):
        """Print summary statistics."""
        logger.info("=" * 50)
        logger.info("STATISTICS")
        logger.info("=" * 50)
        logger.info(f"Total media files found:    {self.stats['total_files']}")
        logger.info(f"Duplicates found:           {self.stats['duplicates_found']}")
        logger.info(f"Duplicates removed:         {self.stats['duplicates_removed']}")
        logger.info(f"Files organized:            {self.stats['files_organized']}")
        logger.info(f"Empty folders removed:      {self.stats['empty_folders_removed']}")
        logger.info(f"Space freed:                {get_file_size_readable(self.stats['space_freed'])}")
        logger.info(f"Errors encountered:         {self.stats['errors']}")
        logger.info("=" * 50)

        # Print date extraction stats
        date_stats = self.date_extractor.get_stats()
        logger.info("Date extraction methods:")
        logger.info(f"  EXIF:              {date_stats['exif']}")
        logger.info(f"  Filename:          {date_stats['filename']}")
        logger.info(f"  Modification time: {date_stats['modified']}")
        logger.info(f"  Failed:            {date_stats['failed']}")
        logger.info("=" * 50)
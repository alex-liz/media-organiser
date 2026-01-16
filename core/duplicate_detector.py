"""
Duplicate file detection.
"""

from pathlib import Path
from typing import List, Dict, Set
from collections import defaultdict
from ..utils.file_operations import calculate_file_hash
from ..utils.exceptions import DuplicateDetectionError
from ..utils.logger import get_logger

logger = get_logger(__name__)


class DuplicateDetector:
    """Detect duplicate files based on content hash."""

    def __init__(self):
        """Initialize the duplicate detector."""
        self.hash_map: Dict[str, List[Path]] = defaultdict(list)
        self.duplicates: List[Path] = []

    def scan_files(self, files: List[Path]) -> Dict[str, List[Path]]:
        """
        Scan files and group by hash.

        Args:
            files: List of file paths to scan

        Returns:
            Dictionary mapping hashes to list of file paths

        Raises:
            DuplicateDetectionError: If scanning fails
        """
        try:
            self.hash_map.clear()

            for file_path in files:
                try:
                    file_hash = calculate_file_hash(file_path)
                    self.hash_map[file_hash].append(file_path)
                except Exception as e:
                    logger.warning(f"Skipping file {file_path}: {str(e)}")
                    continue

            logger.info(f"Scanned {len(files)} files, found {len(self.hash_map)} unique hashes")
            return dict(self.hash_map)

        except Exception as e:
            raise DuplicateDetectionError(f"Failed to scan files: {str(e)}")

    def find_duplicates(self) -> List[Path]:
        """
        Find duplicate files (keeping the first occurrence).

        Returns:
            List of duplicate file paths to be removed
        """
        self.duplicates.clear()

        for file_hash, file_list in self.hash_map.items():
            if len(file_list) > 1:
                # Keep the first file, mark others as duplicates
                duplicates_to_remove = file_list[1:]
                self.duplicates.extend(duplicates_to_remove)

                logger.debug(
                    f"Found {len(duplicates_to_remove)} duplicates of {file_list[0]}"
                )

        logger.info(f"Found {len(self.duplicates)} duplicate files")
        return self.duplicates.copy()

    def get_duplicate_groups(self) -> Dict[str, List[Path]]:
        """
        Get groups of duplicate files.

        Returns:
            Dictionary of hash to list of duplicate files
        """
        return {
            file_hash: files
            for file_hash, files in self.hash_map.items()
            if len(files) > 1
        }

    def get_statistics(self) -> dict:
        """
        Get detection statistics.

        Returns:
            Dictionary with statistics
        """
        total_files = sum(len(files) for files in self.hash_map.values())
        unique_files = len(self.hash_map)
        duplicate_count = len(self.duplicates)

        # Calculate space that would be freed
        space_to_free = 0
        for dup_path in self.duplicates:
            try:
                space_to_free += dup_path.stat().st_size
            except:
                pass

        return {
            'total_files': total_files,
            'unique_files': unique_files,
            'duplicate_count': duplicate_count,
            'duplicate_groups': len(self.get_duplicate_groups()),
            'space_to_free': space_to_free
        }
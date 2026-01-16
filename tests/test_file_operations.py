"""
Tests for file operations.
"""

import pytest
from pathlib import Path
from media_organiser.utils.file_operations import (
    validate_path,
    calculate_file_hash,
    safe_move_file,
    safe_delete_file,
    get_unique_filename,
    remove_empty_directories,
    scan_media_files
)
from media_organiser.utils.exceptions import FileOperationError, InvalidPathError


class TestFileOperations:

    def test_validate_path_exists(self, temp_dir):
        """Test path validation for existing path."""
        result = validate_path(temp_dir, must_exist=True)
        assert result == temp_dir

    def test_validate_path_not_exists(self, temp_dir):
        """Test path validation for non-existing path."""
        non_existent = temp_dir / "does_not_exist"
        with pytest.raises(InvalidPathError):
            validate_path(non_existent, must_exist=True)

    def test_calculate_file_hash(self, temp_dir):
        """Test file hash calculation."""
        file_path = temp_dir / "test.txt"
        file_path.write_text("test content")

        hash1 = calculate_file_hash(file_path)
        hash2 = calculate_file_hash(file_path)

        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 hex digest length

    def test_calculate_hash_same_content(self, temp_dir):
        """Test that same content produces same hash."""
        file1 = temp_dir / "file1.txt"
        file2 = temp_dir / "file2.txt"

        file1.write_text("identical content")
        file2.write_text("identical content")

        assert calculate_file_hash(file1) == calculate_file_hash(file2)

    def test_safe_move_file(self, temp_dir):
        """Test safe file move."""
        source = temp_dir / "source.txt"
        source.write_text("test")

        dest = temp_dir / "subdir" / "dest.txt"

        result = safe_move_file(source, dest)

        assert not source.exists()
        assert dest.exists()
        assert result == dest

    def test_safe_move_file_conflict(self, temp_dir):
        """Test file move with naming conflict."""
        source = temp_dir / "source.txt"
        source.write_text("test")

        existing = temp_dir / "dest.txt"
        existing.write_text("existing")

        result = safe_move_file(source, existing, overwrite=False)

        assert existing.exists()
        assert result != existing
        assert result.exists()

    def test_safe_delete_file(self, temp_dir):
        """Test safe file deletion."""
        file_path = temp_dir / "to_delete.txt"
        file_path.write_text("delete me")

        result = safe_delete_file(file_path)

        assert result is True
        assert not file_path.exists()

    def test_get_unique_filename(self, temp_dir):
        """Test unique filename generation."""
        existing = temp_dir / "file.txt"
        existing.write_text("test")

        unique = get_unique_filename(existing)

        assert unique != existing
        assert unique.stem == "file_1"

    def test_remove_empty_directories(self, temp_dir):
        """Test empty directory removal."""
        # Create directory structure
        (temp_dir / "empty1").mkdir()
        (temp_dir / "empty2" / "nested").mkdir(parents=True)
        (temp_dir / "not_empty").mkdir()
        (temp_dir / "not_empty" / "file.txt").write_text("test")

        count = remove_empty_directories(temp_dir)

        assert count >= 2
        assert not (temp_dir / "empty1").exists()
        assert (temp_dir / "not_empty").exists()

    def test_scan_media_files(self, sample_images):
        """Test media file scanning."""
        temp_dir = sample_images[0].parent

        files = scan_media_files(temp_dir)

        assert len(files) == len(sample_images)
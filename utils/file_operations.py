"""
File operation utilities with error handling.
"""

import os
import shutil
from pathlib import Path
from typing import Optional, List
import hashlib
from .exceptions import FileOperationError, InvalidPathError
from .logger import get_logger

logger = get_logger(__name__)


def validate_path(path: Path, must_exist: bool = True) -> Path:
    """
    Validate a path.

    Args:
        path: Path to validate
        must_exist: Whether the path must exist

    Returns:
        Validated Path object

    Raises:
        InvalidPathError: If path is invalid
    """
    try:
        path = Path(path).resolve()

        if must_exist and not path.exists():
            raise InvalidPathError(f"Path does not exist: {path}")

        return path
    except Exception as e:
        raise InvalidPathError(f"Invalid path: {path}. Error: {str(e)}")


def calculate_file_hash(file_path: Path, algorithm: str = 'sha256') -> str:
    """
    Calculate hash of a file.

    Args:
        file_path: Path to the file
        algorithm: Hash algorithm to use

    Returns:
        Hex digest of the file hash

    Raises:
        FileOperationError: If hash calculation fails
    """
    try:
        hash_func = hashlib.new(algorithm)

        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hash_func.update(chunk)

        return hash_func.hexdigest()

    except PermissionError:
        raise FileOperationError(f"Permission denied reading file: {file_path}")
    except FileNotFoundError:
        raise FileOperationError(f"File not found: {file_path}")
    except Exception as e:
        raise FileOperationError(f"Failed to calculate hash for {file_path}: {str(e)}")


def safe_move_file(source: Path, destination: Path, overwrite: bool = False) -> Path:
    """
    Safely move a file with conflict resolution.

    Args:
        source: Source file path
        destination: Destination file path
        overwrite: Whether to overwrite existing files

    Returns:
        Final destination path

    Raises:
        FileOperationError: If move operation fails
    """
    try:
        source = validate_path(source, must_exist=True)
        destination = Path(destination)

        # Create destination directory
        destination.parent.mkdir(parents=True, exist_ok=True)

        # Handle filename conflicts
        if destination.exists() and not overwrite:
            destination = get_unique_filename(destination)

        shutil.move(str(source), str(destination))
        logger.debug(f"Moved file: {source} -> {destination}")

        return destination

    except PermissionError:
        raise FileOperationError(f"Permission denied moving file: {source} -> {destination}")
    except shutil.Error as e:
        raise FileOperationError(f"Failed to move file: {source} -> {destination}. Error: {str(e)}")
    except Exception as e:
        raise FileOperationError(f"Unexpected error moving file: {source}. Error: {str(e)}")


def safe_copy_file(source: Path, destination: Path, overwrite: bool = False) -> Path:
    """
    Safely copy a file with conflict resolution.

    Args:
        source: Source file path
        destination: Destination file path
        overwrite: Whether to overwrite existing files

    Returns:
        Final destination path

    Raises:
        FileOperationError: If copy operation fails
    """
    try:
        source = validate_path(source, must_exist=True)
        destination = Path(destination)

        destination.parent.mkdir(parents=True, exist_ok=True)

        if destination.exists() and not overwrite:
            destination = get_unique_filename(destination)

        shutil.copy2(str(source), str(destination))
        logger.debug(f"Copied file: {source} -> {destination}")

        return destination

    except PermissionError:
        raise FileOperationError(f"Permission denied copying file: {source}")
    except Exception as e:
        raise FileOperationError(f"Failed to copy file: {source}. Error: {str(e)}")


def safe_delete_file(file_path: Path, secure: bool = False) -> bool:
    """
    Safely delete a file.

    Args:
        file_path: Path to the file
        secure: Whether to use secure deletion

    Returns:
        True if deletion was successful

    Raises:
        FileOperationError: If deletion fails
    """
    try:
        file_path = validate_path(file_path, must_exist=True)

        if secure:
            # Overwrite file before deletion
            file_size = file_path.stat().st_size
            with open(file_path, 'wb') as f:
                f.write(os.urandom(file_size))

        file_path.unlink()
        logger.debug(f"Deleted file: {file_path}")

        return True

    except PermissionError:
        raise FileOperationError(f"Permission denied deleting file: {file_path}")
    except Exception as e:
        raise FileOperationError(f"Failed to delete file: {file_path}. Error: {str(e)}")


def get_unique_filename(file_path: Path) -> Path:
    """
    Generate a unique filename by appending a number.

    Args:
        file_path: Original file path

    Returns:
        Unique file path
    """
    counter = 1
    stem = file_path.stem
    suffix = file_path.suffix
    parent = file_path.parent

    while file_path.exists():
        file_path = parent / f"{stem}_{counter}{suffix}"
        counter += 1

    return file_path


def remove_empty_directories(root_path: Path) -> int:
    """
    Remove empty directories recursively.

    Args:
        root_path: Root directory to start from

    Returns:
        Number of directories removed
    """
    removed_count = 0

    try:
        root_path = validate_path(root_path, must_exist=True)

        for dirpath, dirnames, filenames in os.walk(str(root_path), topdown=False):
            current_dir = Path(dirpath)

            # Skip if directory doesn't exist (may have been removed)
            if not current_dir.exists():
                continue

            # Check if directory is empty or contains only .DS_Store
            contents = list(current_dir.iterdir())
            is_empty = len(contents) == 0
            only_ds_store = len(contents) == 1 and contents[0].name == '.DS_Store'

            if is_empty or only_ds_store:
                try:
                    if only_ds_store:
                        contents[0].unlink()
                    current_dir.rmdir()
                    removed_count += 1
                    logger.debug(f"Removed empty directory: {current_dir}")
                except Exception as e:
                    logger.warning(f"Could not remove directory {current_dir}: {str(e)}")

        return removed_count

    except Exception as e:
        logger.error(f"Error removing empty directories: {str(e)}")
        return removed_count


def get_file_size_readable(size_bytes: int) -> str:
    """
    Convert bytes to human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Human-readable size string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def scan_media_files(root_path: Path, extensions: Optional[List[str]] = None) -> List[Path]:
    """
    Scan directory for media files.

    Args:
        root_path: Root directory to scan
        extensions: List of file extensions to include (e.g., ['.jpg', '.mp4'])

    Returns:
        List of media file paths

    Raises:
        InvalidPathError: If root path is invalid
    """
    if extensions is None:
        extensions = [
            # Images
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.heic',
            # Videos
            '.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v'
        ]

    extensions = [ext.lower() for ext in extensions]
    media_files = []

    try:
        root_path = validate_path(root_path, must_exist=True)

        for file_path in root_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in extensions:
                media_files.append(file_path)

        logger.info(f"Found {len(media_files)} media files in {root_path}")
        return media_files

    except Exception as e:
        raise InvalidPathError(f"Failed to scan directory {root_path}: {str(e)}")

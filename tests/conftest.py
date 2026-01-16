"""
Pytest configuration and fixtures.
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from datetime import datetime


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_images(temp_dir):
    """Create sample image files for testing."""
    images = []

    # Create some test files
    for i in range(5):
        file_path = temp_dir / f"IMG_{i:04d}.jpg"
        file_path.write_bytes(b"fake image data " * (i + 1))
        images.append(file_path)

    return images


@pytest.fixture
def duplicate_files(temp_dir):
    """Create duplicate files for testing."""
    original = temp_dir / "original.jpg"
    original.write_bytes(b"test content")

    duplicate1 = temp_dir / "duplicate1.jpg"
    duplicate1.write_bytes(b"test content")

    duplicate2 = temp_dir / "subfolder" / "duplicate2.jpg"
    duplicate2.parent.mkdir(parents=True, exist_ok=True)
    duplicate2.write_bytes(b"test content")

    return [original, duplicate1, duplicate2]
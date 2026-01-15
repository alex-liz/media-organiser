import os
import shutil
import hashlib
from pathlib import Path
from collections import defaultdict


def get_file_hash(filepath):
    """Calculate MD5 hash of a file to identify duplicates."""
    hash_md5 = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        print(f"Error hashing {filepath}: {e}")
        return None


def is_photo_file(filename):
    """Check if file is a photo based on extension."""
    photo_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff',
                        '.tif', '.webp', '.heic', '.heif', '.raw', '.cr2',
                        '.nef', '.arw', '.dng'}
    return Path(filename).suffix.lower() in photo_extensions


def is_video_file(filename):
    """Check if file is a video based on extension."""
    video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv',
                        '.webm', '.m4v', '.mpg', '.mpeg', '.3gp', '.mts',
                        '.m2ts', '.vob'}
    return Path(filename).suffix.lower() in video_extensions


def is_media_file(filename):
    """Check if file is a photo or video."""
    return is_photo_file(filename) or is_video_file(filename)


def consolidate_media(source_dir, dest_dir, include_videos=True):
    """
    Move all photo files (and optionally video files) from source_dir
    (including subfolders) to dest_dir.
    Removes duplicates based on file content (hash).
    """
    source_path = Path(source_dir)
    dest_path = Path(dest_dir)

    # Create destination directory if it doesn't exist
    dest_path.mkdir(parents=True, exist_ok=True)

    # Track file hashes to detect duplicates
    file_hashes = defaultdict(list)

    # Statistics
    stats = {
        'total_found': 0,
        'photos_found': 0,
        'videos_found': 0,
        'moved': 0,
        'photos_moved': 0,
        'videos_moved': 0,
        'duplicates': 0,
        'errors': 0
    }

    media_type = "photos and videos" if include_videos else "photos"
    print(f"Scanning for {media_type} in: {source_path}")
    print(f"Destination folder: {dest_path}")
    print("-" * 60)

    # Find all media files
    media_files = []
    for root, dirs, files in os.walk(source_path):
        for file in files:
            filepath = Path(root) / file
            is_photo = is_photo_file(file)
            is_video = is_video_file(file)

            if is_photo or (is_video and include_videos):
                media_files.append(filepath)
                stats['total_found'] += 1

                if is_photo:
                    stats['photos_found'] += 1
                elif is_video:
                    stats['videos_found'] += 1

    if include_videos:
        print(
            f"Found {stats['total_found']} media files ({stats['photos_found']} photos, {stats['videos_found']} videos)")
    else:
        print(f"Found {stats['total_found']} photo files")

    print("Processing files...")
    print("-" * 60)

    # Process each media file
    for filepath in media_files:
        try:
            # Determine file type
            is_photo = is_photo_file(filepath.name)
            file_type = "PHOTO" if is_photo else "VIDEO"

            # Calculate hash
            file_hash = get_file_hash(filepath)

            if file_hash is None:
                stats['errors'] += 1
                continue

            # Check if this file content already exists
            if file_hash in file_hashes:
                print(f"DUPLICATE [{file_type}]: {filepath.name} (same as {file_hashes[file_hash][0].name})")
                stats['duplicates'] += 1
                continue

            # Generate unique filename if name collision exists
            dest_file = dest_path / filepath.name
            counter = 1
            original_stem = filepath.stem
            original_suffix = filepath.suffix

            while dest_file.exists():
                dest_file = dest_path / f"{original_stem}_{counter}{original_suffix}"
                counter += 1

            # Move file
            shutil.move(str(filepath), str(dest_file))
            file_hashes[file_hash].append(dest_file)
            stats['moved'] += 1

            if is_photo:
                stats['photos_moved'] += 1
            else:
                stats['videos_moved'] += 1

            print(f"MOVED [{file_type}]: {filepath.name} -> {dest_file.name}")

        except Exception as e:
            print(f"ERROR processing {filepath}: {e}")
            stats['errors'] += 1

    # Print summary
    print("-" * 60)
    print("SUMMARY:")
    if include_videos:
        print(
            f"Total media found: {stats['total_found']} ({stats['photos_found']} photos, {stats['videos_found']} videos)")
        print(f"Media moved: {stats['moved']} ({stats['photos_moved']} photos, {stats['videos_moved']} videos)")
    else:
        print(f"Total photos found: {stats['total_found']}")
        print(f"Photos moved: {stats['moved']}")
    print(f"Duplicates skipped: {stats['duplicates']}")
    print(f"Errors: {stats['errors']}")
    print(f"\nAll media consolidated in: {dest_path}")


if __name__ == "__main__":
    # Example usage - modify these paths
    source_directory = input("Enter source directory path: ").strip()
    destination_directory = input("Enter destination directory path: ").strip()

    # Ask if user wants to include videos
    include_videos_input = input("Include videos? (yes/no, default: yes): ").strip().lower()
    include_videos = include_videos_input in ['yes', 'y', ''] or include_videos_input == ''

    if not os.path.exists(source_directory):
        print(f"Error: Source directory '{source_directory}' does not exist!")
    else:
        consolidate_media(source_directory, destination_directory, include_videos)

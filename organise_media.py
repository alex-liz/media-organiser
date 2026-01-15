import os
import shutil
import re
from pathlib import Path
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS


def extract_date_from_filename(filename):
    """Extract date from filename using common date patterns."""
    # Common date patterns in filenames
    patterns = [
        r'(\d{4})[-_](\d{2})[-_](\d{2})',  # YYYY-MM-DD or YYYY_MM_DD
        r'(\d{4})(\d{2})(\d{2})',  # YYYYMMDD
        r'(\d{2})[-_](\d{2})[-_](\d{4})',  # DD-MM-YYYY or DD_MM_YYYY
        r'(\d{2})(\d{2})(\d{4})',  # DDMMYYYY
        r'IMG[-_](\d{4})(\d{2})(\d{2})',  # IMG_YYYYMMDD
        r'VID[-_](\d{4})(\d{2})(\d{2})',  # VID_YYYYMMDD
        r'(\d{4})[-_](\d{2})',  # YYYY-MM or YYYY_MM
    ]

    for pattern in patterns:
        match = re.search(pattern, filename)
        if match:
            groups = match.groups()
            try:
                # Try YYYY-MM-DD format
                if len(groups[0]) == 4:
                    year, month = int(groups[0]), int(groups[1])
                    day = int(groups[2]) if len(groups) > 2 else 1
                # Try DD-MM-YYYY format
                elif len(groups[2]) == 4:
                    day, month, year = int(groups[0]), int(groups[1]), int(groups[2])
                # Try YYYY-MM format
                else:
                    year, month = int(groups[0]), int(groups[1])
                    day = 1

                if 1 <= month <= 12 and 1 <= day <= 31 and 1900 <= year <= 2100:
                    return datetime(year, month, day)
            except (ValueError, IndexError):
                continue

    return None


def get_exif_date(filepath):
    """Extract date from EXIF metadata (for images)."""
    try:
        image = Image.open(filepath)
        exifdata = image.getexif()

        # Common EXIF date tags
        date_tags = ['DateTimeOriginal', 'DateTime', 'DateTimeDigitized']

        for tag_id, value in exifdata.items():
            tag_name = TAGS.get(tag_id, tag_id)

            if tag_name in date_tags and value:
                # EXIF date format: 'YYYY:MM:DD HH:MM:SS'
                try:
                    date_str = str(value).split()[0]  # Get date part only
                    date_obj = datetime.strptime(date_str, '%Y:%m:%d')
                    return date_obj
                except (ValueError, IndexError):
                    continue

    except Exception:
        pass

    return None


def get_video_metadata_date(filepath):
    """Extract date from video metadata using file's metadata."""
    try:
        # Try to import ffmpeg-python for better video metadata extraction
        try:
            import ffmpeg
            probe = ffmpeg.probe(str(filepath))

            # Check for creation_time in format section
            if 'format' in probe and 'tags' in probe['format']:
                tags = probe['format']['tags']

                # Common video date tags
                date_keys = ['creation_time', 'date', 'DATE']

                for key in date_keys:
                    if key in tags:
                        date_str = tags[key]
                        # Parse ISO format: 2024-03-15T10:30:00.000000Z
                        try:
                            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                            return date_obj
                        except:
                            try:
                                # Try other common formats
                                date_obj = datetime.strptime(date_str[:10], '%Y-%m-%d')
                                return date_obj
                            except:
                                continue
        except ImportError:
            # ffmpeg-python not available, continue to file date
            pass

    except Exception:
        pass

    return None


def get_file_creation_date(filepath):
    """Get file creation/modification date as fallback."""
    try:
        # Use the earlier of creation or modification time
        stat = os.stat(filepath)
        timestamp = min(stat.st_ctime, stat.st_mtime)
        return datetime.fromtimestamp(timestamp)
    except Exception:
        return None


def get_media_date(filepath):
    """
    Get media file date by checking (in order):
    1. Date in filename
    2. EXIF metadata (for images)
    3. Video metadata (for videos)
    4. File creation/modification date
    """
    filename = filepath.name
    file_ext = filepath.suffix.lower()

    # Try filename first
    date = extract_date_from_filename(filename)
    if date:
        return date, "filename"

    # Try EXIF metadata for images
    if is_photo_file(filename):
        date = get_exif_date(filepath)
        if date:
            return date, "EXIF"

    # Try video metadata for videos
    if is_video_file(filename):
        date = get_video_metadata_date(filepath)
        if date:
            return date, "video_metadata"

    # Fallback to file dates
    date = get_file_creation_date(filepath)
    if date:
        return date, "file_date"

    return None, "unknown"


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


def organize_media_by_date(source_dir):
    """
    Organize photos and videos into folders by year and month (YYYY-MM format).
    """
    source_path = Path(source_dir)

    if not source_path.exists():
        print(f"Error: Source directory '{source_dir}' does not exist!")
        return

    # Statistics
    stats = {
        'total': 0,
        'photos': 0,
        'videos': 0,
        'organized': 0,
        'filename_date': 0,
        'exif_date': 0,
        'video_metadata_date': 0,
        'file_date': 0,
        'no_date': 0,
        'errors': 0
    }

    print(f"Organizing media files in: {source_path}")
    print("-" * 60)

    # Find all media files in the source directory
    media_files = [f for f in source_path.iterdir()
                   if f.is_file() and is_media_file(f.name)]

    stats['total'] = len(media_files)
    stats['photos'] = sum(1 for f in media_files if is_photo_file(f.name))
    stats['videos'] = sum(1 for f in media_files if is_video_file(f.name))

    print(f"Found {stats['total']} media files ({stats['photos']} photos, {stats['videos']} videos)")
    print("Processing...")
    print("-" * 60)

    for filepath in media_files:
        try:
            # Determine file type
            file_type = "PHOTO" if is_photo_file(filepath.name) else "VIDEO"

            # Get media date
            date, source_type = get_media_date(filepath)

            if date is None:
                print(f"NO DATE: [{file_type}] {filepath.name} - Skipping")
                stats['no_date'] += 1
                continue

            # Create year-month folder name (e.g., "2024-03")
            folder_name = date.strftime("%Y-%m")
            dest_folder = source_path / folder_name

            # Create destination folder if it doesn't exist
            dest_folder.mkdir(exist_ok=True)

            # Handle filename conflicts - never overwrite existing files
            dest_file = dest_folder / filepath.name
            counter = 1
            original_stem = filepath.stem
            original_suffix = filepath.suffix

            # Keep incrementing counter until we find a unique filename
            while dest_file.exists():
                # If file is already in the correct location, skip it
                if dest_file == filepath:
                    break
                dest_file = dest_folder / f"{original_stem}_{counter}{original_suffix}"
                counter += 1

            # Move file only if it's not already in the correct location
            if dest_file != filepath and not dest_file.exists():
                shutil.move(str(filepath), str(dest_file))
                print(f"MOVED: [{file_type}] {filepath.name} -> {folder_name}/ (from {source_type})")
                stats['organized'] += 1

                # Update source type stats
                if source_type == "filename":
                    stats['filename_date'] += 1
                elif source_type == "EXIF":
                    stats['exif_date'] += 1
                elif source_type == "video_metadata":
                    stats['video_metadata_date'] += 1
                elif source_type == "file_date":
                    stats['file_date'] += 1
            else:
                print(f"ALREADY IN PLACE: [{file_type}] {filepath.name} in {folder_name}/")
                stats['organized'] += 1
                if source_type == "filename":
                    stats['filename_date'] += 1
                elif source_type == "EXIF":
                    stats['exif_date'] += 1
                elif source_type == "video_metadata":
                    stats['video_metadata_date'] += 1
                elif source_type == "file_date":
                    stats['file_date'] += 1

        except Exception as e:
            print(f"ERROR processing {filepath.name}: {e}")
            stats['errors'] += 1

    # Print summary
    print("-" * 60)
    print("SUMMARY:")
    print(f"Total media files: {stats['total']} ({stats['photos']} photos, {stats['videos']} videos)")
    print(f"Successfully organized: {stats['organized']}")
    print(f"  - From filename: {stats['filename_date']}")
    print(f"  - From EXIF: {stats['exif_date']}")
    print(f"  - From video metadata: {stats['video_metadata_date']}")
    print(f"  - From file date: {stats['file_date']}")
    print(f"No date found: {stats['no_date']}")
    print(f"Errors: {stats['errors']}")
    print(f"\nMedia files organized in: {source_path}")


if __name__ == "__main__":
    source_directory = input("Enter directory with photos/videos to organize: ").strip()

    print("\nThis script will organize photos and videos into YYYY-MM folders.")
    print("Media will be organized based on:")
    print("  1. Date in filename (if found)")
    print("  2. EXIF metadata (for photos)")
    print("  3. Video metadata (for videos)")
    print("  4. File creation date (as fallback)")
    print("\nNote: For better video metadata extraction, install ffmpeg-python:")
    print("      pip install ffmpeg-python")
    confirm = input("\nContinue? (yes/no): ").strip().lower()

    if confirm in ['yes', 'y']:
        organize_media_by_date(source_directory)
    else:
        print("Operation cancelled.")

#!/usr/bin/env python3
"""
Media File Organizer and Duplicate Remover
Organizes photos and videos by date and removes duplicates
"""

import os
import sys
import hashlib
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import re

try:
    from PIL import Image
    from PIL.ExifTags import TAGS

    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    print("Warning: Pillow not installed. EXIF data reading will be limited.")
    print("Install with: pip install Pillow")


class MediaOrganizer:
    def __init__(self, path, organize_mode='none', remove_duplicates=False, dry_run=False):
        self.path = Path(path)
        self.organize_mode = organize_mode
        self.should_remove_duplicates = remove_duplicates
        self.dry_run = dry_run

        # Statistics
        self.stats = {
            'total_files': 0,
            'duplicates_found': 0,
            'duplicates_removed': 0,
            'files_organized': 0,
            'empty_folders_removed': 0,
            'errors': 0,
            'space_freed': 0
        }

        # Supported extensions
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.heic'}
        self.video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v'}
        self.media_extensions = self.image_extensions | self.video_extensions

    def get_file_hash(self, filepath):
        """Calculate SHA256 hash of a file"""
        sha256_hash = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            print(f"Error hashing {filepath}: {e}")
            self.stats['errors'] += 1
            return None

    def get_exif_date(self, filepath):
        """Extract date from EXIF data"""
        if not PILLOW_AVAILABLE:
            return None

        try:
            image = Image.open(filepath)
            exifdata = image.getexif()

            # Look for DateTimeOriginal (36867) or DateTime (306)
            for tag_id in [36867, 306]:
                if tag_id in exifdata:
                    date_str = exifdata[tag_id]
                    # EXIF date format: "YYYY:MM:DD HH:MM:SS"
                    return datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
        except Exception:
            pass

        return None

    def extract_date_from_filename(self, filename):
        """Extract date from filename using common patterns"""
        patterns = [
            r'(\d{4})[_-](\d{2})[_-](\d{2})',  # YYYY-MM-DD or YYYY_MM_DD
            r'(\d{4})(\d{2})(\d{2})',  # YYYYMMDD
            r'(\d{2})[_-](\d{2})[_-](\d{4})',  # DD-MM-YYYY or DD_MM_YYYY
            r'IMG[_-](\d{4})(\d{2})(\d{2})',  # IMG_YYYYMMDD
        ]

        for pattern in patterns:
            match = re.search(pattern, filename)
            if match:
                groups = match.groups()
                try:
                    if len(groups[0]) == 4:  # YYYY first
                        year, month, day = int(groups[0]), int(groups[1]), int(groups[2])
                    else:  # DD first
                        day, month, year = int(groups[0]), int(groups[1]), int(groups[2])

                    return datetime(year, month, day)
                except ValueError:
                    continue

        return None

    def get_file_date(self, filepath):
        """Get file date from EXIF, filename, or modification time"""
        # Try EXIF data first for images
        if filepath.suffix.lower() in self.image_extensions:
            exif_date = self.get_exif_date(filepath)
            if exif_date:
                return exif_date

        # Try filename
        filename_date = self.extract_date_from_filename(filepath.name)
        if filename_date:
            return filename_date

        # Fall back to file modification time
        try:
            timestamp = os.path.getmtime(filepath)
            return datetime.fromtimestamp(timestamp)
        except Exception:
            return datetime.now()

    def find_duplicates(self):
        """Find duplicate files based on hash and filename"""
        print("\n🔍 Scanning for duplicates...")

        hash_dict = defaultdict(list)
        name_dict = defaultdict(list)

        for filepath in self.path.rglob('*'):
            if filepath.is_file() and filepath.suffix.lower() in self.media_extensions:
                self.stats['total_files'] += 1

                # Check by hash
                file_hash = self.get_file_hash(filepath)
                if file_hash:
                    hash_dict[file_hash].append(filepath)

                # Check by name
                name_dict[filepath.name].append(filepath)

        # Find duplicates
        duplicates = []

        # Hash-based duplicates (exact copies)
        for file_hash, files in hash_dict.items():
            if len(files) > 1:
                # Keep the first one, mark others as duplicates
                duplicates.extend(files[1:])
                self.stats['duplicates_found'] += len(files) - 1

        return duplicates

    def remove_duplicates(self, duplicates):
        """Remove duplicate files"""
        print(f"\n🗑️  Removing {len(duplicates)} duplicate(s)...")

        for filepath in duplicates:
            try:
                file_size = filepath.stat().st_size

                if self.dry_run:
                    print(f"[DRY RUN] Would remove: {filepath}")
                else:
                    filepath.unlink()
                    print(f"Removed: {filepath}")
                    self.stats['duplicates_removed'] += 1
                    self.stats['space_freed'] += file_size
            except Exception as e:
                print(f"Error removing {filepath}: {e}")
                self.stats['errors'] += 1

    def organize_files(self):
        """Organize files by date into folders"""
        if self.organize_mode == 'none':
            return

        print(f"\n📁 Organizing files by {self.organize_mode}...")

        for filepath in self.path.rglob('*'):
            if filepath.is_file() and filepath.suffix.lower() in self.media_extensions:
                file_date = self.get_file_date(filepath)

                # Determine target folder based on mode
                if self.organize_mode == 'year':
                    target_folder = self.path / str(file_date.year)
                elif self.organize_mode == 'year_month':
                    target_folder = self.path / str(file_date.year) / f"{file_date.month:02d}"
                elif self.organize_mode == 'year_month_day':
                    target_folder = self.path / str(file_date.year) / f"{file_date.month:02d}" / f"{file_date.day:02d}"
                else:
                    continue

                # Skip if already in correct location
                if filepath.parent == target_folder:
                    continue

                # Create target folder
                if not self.dry_run:
                    target_folder.mkdir(parents=True, exist_ok=True)

                # Move file
                target_path = target_folder / filepath.name

                # Handle name conflicts
                counter = 1
                while target_path.exists():
                    stem = filepath.stem
                    target_path = target_folder / f"{stem}_{counter}{filepath.suffix}"
                    counter += 1

                try:
                    if self.dry_run:
                        print(f"[DRY RUN] Would move: {filepath} -> {target_path}")
                    else:
                        filepath.rename(target_path)
                        print(f"Moved: {filepath.name} -> {target_folder}")
                        self.stats['files_organized'] += 1
                except Exception as e:
                    print(f"Error moving {filepath}: {e}")
                    self.stats['errors'] += 1

    def remove_empty_folders(self):
        """Remove empty folders recursively, including all nested empty subfolders"""
        print("\n🗂️  Removing empty folders...")

        removed_count = 0

        # Keep checking until no more empty folders are found
        changed = True
        while changed:
            changed = False

            # Walk the directory tree from bottom to top
            for root, dirs, files in os.walk(self.path, topdown=False):
                # Skip the root directory itself
                if root == str(self.path):
                    continue

                try:
                    # Get contents of the directory
                    contents = os.listdir(root)

                    # Check if directory is empty OR only contains .DS_Store
                    is_empty = len(contents) == 0
                    only_ds_store = (len(contents) == 1 and contents[0] == '.DS_Store')

                    if is_empty or only_ds_store:
                        # If only .DS_Store exists, remove it first
                        if only_ds_store:
                            ds_store_path = os.path.join(root, '.DS_Store')
                            if self.dry_run:
                                print(f"[DRY RUN] Would remove .DS_Store: {ds_store_path}")
                            else:
                                os.remove(ds_store_path)
                                print(f"Removed .DS_Store: {ds_store_path}")

                        # Now remove the empty folder
                        if self.dry_run:
                            print(f"[DRY RUN] Would remove empty folder: {root}")
                        else:
                            os.rmdir(root)
                            print(f"Removed empty folder: {root}")
                            self.stats['empty_folders_removed'] += 1

                        removed_count += 1
                        changed = True  # We made a change, need another pass

                except FileNotFoundError:
                    # Folder was already removed, skip
                    pass
                except PermissionError as e:
                    print(f"Permission error on {root}: {e}")
                    self.stats['errors'] += 1
                except Exception as e:
                    print(f"Error removing folder {root}: {e}")
                    self.stats['errors'] += 1

        if removed_count == 0:
            print("No empty folders found.")
        else:
            print(f"✅ Total empty folders removed: {removed_count}")

    def print_statistics(self):
        """Print final statistics"""
        print("\n" + "=" * 50)
        print("📊 STATISTICS")
        print("=" * 50)
        print(f"Total media files found:    {self.stats['total_files']}")
        print(f"Duplicates found:           {self.stats['duplicates_found']}")
        print(f"Duplicates removed:         {self.stats['duplicates_removed']}")
        print(f"Files organized:            {self.stats['files_organized']}")
        print(f"Empty folders removed:      {self.stats['empty_folders_removed']}")
        print(f"Space freed:                {self.stats['space_freed'] / 1024 / 1024:.2f} MB")
        print(f"Errors encountered:         {self.stats['errors']}")
        print("=" * 50)

    def run(self):
        """Main execution method"""
        if not self.path.exists():
            print(f"Error: Path '{self.path}' does not exist!")
            return

        if not self.path.is_dir():
            print(f"Error: '{self.path}' is not a directory!")
            return

        print(f"\n🎬 Starting Media Organizer")
        print(f"Path: {self.path}")
        print(f"Remove duplicates: {self.should_remove_duplicates}")
        print(f"Organize by: {self.organize_mode}")
        print(f"Dry run: {self.dry_run}")

        # Find and remove duplicates
        if self.should_remove_duplicates:
            duplicates = self.find_duplicates()
            if duplicates:
                self.remove_duplicates(duplicates)
            else:
                print("\n✅ No duplicates found!")

        # Organize files
        self.organize_files()

        # Remove empty folders (after organizing, there might be empty folders left)
        self.remove_empty_folders()

        # Print statistics
        self.print_statistics()


def show_menu():
    """Display interactive menu"""
    print("\n" + "=" * 50)
    print("📸 MEDIA FILE ORGANIZER & DUPLICATE REMOVER")
    print("=" * 50)

    print("\n1. Remove duplicates?")
    print("   [y] Yes")
    print("   [n] No (default)")
    remove_dups = input("   Choice: ").strip().lower() == 'y'

    print("\n2. How to organize files by date?")
    print("   [1] Don't organize (default)")
    print("   [2] By year (YYYY)")
    print("   [3] By year and month (YYYY/MM)")
    print("   [4] By year, month, and day (YYYY/MM/DD)")

    org_choice = input("   Choice: ").strip()
    organize_modes = {
        '1': 'none',
        '2': 'year',
        '3': 'year_month',
        '4': 'year_month_day'
    }
    organize_mode = organize_modes.get(org_choice, 'none')

    print("\n3. Perform dry run? (show what would be done without making changes)")
    print("   [y] Yes (recommended for first run)")
    print("   [n] No (default)")
    dry_run = input("   Choice: ").strip().lower() == 'y'

    return remove_dups, organize_mode, dry_run


def main():
    parser = argparse.ArgumentParser(description='Organize media files and remove duplicates')
    parser.add_argument('path', nargs='?', help='Path to folder to process')
    parser.add_argument('--no-menu', action='store_true', help='Skip interactive menu')
    parser.add_argument('--remove-duplicates', action='store_true', help='Remove duplicate files')
    parser.add_argument('--organize', choices=['none', 'year', 'year_month', 'year_month_day'],
                        default='none', help='Organization mode')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')

    args = parser.parse_args()

    # Get path
    if args.path:
        path = args.path
    else:
        path = input("\nEnter folder path to process: ").strip()

    if not path:
        print("Error: No path provided!")
        sys.exit(1)

    # Get options
    if args.no_menu:
        remove_dups = args.remove_duplicates
        organize_mode = args.organize
        dry_run = args.dry_run
    else:
        remove_dups, organize_mode, dry_run = show_menu()

    # Confirmation
    print("\n" + "=" * 50)
    print("⚠️  CONFIRM SETTINGS")
    print("=" * 50)
    print(f"Path: {path}")
    print(f"Remove duplicates: {remove_dups}")
    print(f"Organize by: {organize_mode}")
    print(f"Dry run: {dry_run}")

    if not dry_run:
        confirm = input("\nProceed? [y/N]: ").strip().lower()
        if confirm != 'y':
            print("Cancelled.")
            return

    # Run organizer
    organizer = MediaOrganizer(path, organize_mode, remove_dups, dry_run)
    organizer.run()

    print("\n✅ Complete!")


if __name__ == "__main__":
    main()
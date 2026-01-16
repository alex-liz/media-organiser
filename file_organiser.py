#!/usr/bin/env python3

"""
Media File Organizer and Duplicate Remover
Organizes photos and videos by date and removes duplicates
"""

import os
import hashlib
import time
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
    print("Warning: Pillow not installed.\nEXIF data reading will be limited.")
    print("Install with: pip install Pillow")


class MediaOrganizer:
    def __init__(
            self,
            path,
            organize_mode='none',
            remove_duplicates=False,
            dry_run=False,
            progress_callback=None,
            cancel_callback=None
    ):
        self.path = Path(path)
        self.organize_mode = organize_mode
        self.should_remove_duplicates = remove_duplicates
        self.dry_run = dry_run

        # Optional UI hooks
        self.progress_callback = progress_callback
        self.cancel_callback = cancel_callback

        # Progress tracking
        self.total_steps = 0
        self.completed_steps = 0
        self.start_time = None

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
        self.image_extensions = {
            '.jpg', '.jpeg', '.png', '.gif',
            '.bmp', '.tiff', '.webp', '.heic'
        }
        self.video_extensions = {
            '.mp4', '.avi', '.mov', '.mkv',
            '.wmv', '.flv', '.webm', '.m4v'
        }
        self.media_extensions = self.image_extensions | self.video_extensions

    # --------------------------------------------------
    # Internal helpers
    # --------------------------------------------------
    def _cancel_requested(self):
        return self.cancel_callback and self.cancel_callback()

    def _report_progress(self):
        self.completed_steps += 1

        if not self.progress_callback or not self.total_steps:
            return

        elapsed = time.time() - self.start_time
        rate = elapsed / self.completed_steps if self.completed_steps else 0
        remaining = self.total_steps - self.completed_steps
        eta_seconds = int(rate * remaining)

        self.progress_callback(
            self.completed_steps,
            self.total_steps,
            eta_seconds
        )

    # --------------------------------------------------
    # Core helpers
    # --------------------------------------------------
    def get_file_hash(self, filepath):
        sha256_hash = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                for block in iter(lambda: f.read(4096), b""):
                    if self._cancel_requested():
                        return None
                    sha256_hash.update(block)
            return sha256_hash.hexdigest()
        except Exception as e:
            print(f"Error hashing {filepath}: {e}")
            self.stats['errors'] += 1
            return None

    def get_exif_date(self, filepath):
        if not PILLOW_AVAILABLE:
            return None
        try:
            image = Image.open(filepath)
            exifdata = image.getexif()
            for tag_id in [36867, 306]:
                if tag_id in exifdata:
                    return datetime.strptime(exifdata[tag_id], "%Y:%m:%d %H:%M:%S")
        except Exception:
            pass
        return None

    def extract_date_from_filename(self, filename):
        patterns = [
            r'(\d{4})[_-](\d{2})[_-](\d{2})',
            r'(\d{4})(\d{2})(\d{2})',
            r'(\d{2})[_-](\d{2})[_-](\d{4})',
            r'IMG[_-](\d{4})(\d{2})(\d{2})',
        ]
        for pattern in patterns:
            match = re.search(pattern, filename)
            if match:
                try:
                    g = match.groups()
                    if len(g[0]) == 4:
                        return datetime(int(g[0]), int(g[1]), int(g[2]))
                    return datetime(int(g[2]), int(g[1]), int(g[0]))
                except ValueError:
                    pass
        return None

    def get_file_date(self, filepath):
        if filepath.suffix.lower() in self.image_extensions:
            exif_date = self.get_exif_date(filepath)
            if exif_date:
                return exif_date

        filename_date = self.extract_date_from_filename(filepath.name)
        if filename_date:
            return filename_date

        return datetime.fromtimestamp(filepath.stat().st_mtime)

    # --------------------------------------------------
    # Processing phases
    # --------------------------------------------------
    def find_duplicates(self):
        print("\n🔍 Scanning for duplicates...")
        hash_dict = defaultdict(list)

        for filepath in self.path.rglob('*'):
            if self._cancel_requested():
                return []

            if filepath.is_file() and filepath.suffix.lower() in self.media_extensions:
                self.stats['total_files'] += 1
                file_hash = self.get_file_hash(filepath)
                if file_hash:
                    hash_dict[file_hash].append(filepath)
                self._report_progress()

        duplicates = []
        for files in hash_dict.values():
            if len(files) > 1:
                duplicates.extend(files[1:])
                self.stats['duplicates_found'] += len(files) - 1

        return duplicates

    def remove_duplicates(self, duplicates):
        print(f"\n🗑 Removing {len(duplicates)} duplicate(s)...")
        for filepath in duplicates:
            if self._cancel_requested():
                return

            try:
                size = filepath.stat().st_size
                if self.dry_run:
                    print(f"[DRY RUN] Would remove: {filepath}")
                else:
                    filepath.unlink()
                    print(f"Removed: {filepath}")
                self.stats['duplicates_removed'] += 1
                self.stats['space_freed'] += size
            except Exception as e:
                print(f"Error removing {filepath}: {e}")
                self.stats['errors'] += 1

            self._report_progress()

    def organize_files(self):
        if self.organize_mode == 'none':
            return

        print(f"\n📂 Organizing files by {self.organize_mode}...")
        for filepath in self.path.rglob('*'):
            if self._cancel_requested():
                return

            if filepath.is_file() and filepath.suffix.lower() in self.media_extensions:
                date = self.get_file_date(filepath)

                if self.organize_mode == 'year':
                    target = self.path / str(date.year)
                elif self.organize_mode == 'year_month':
                    target = self.path / str(date.year) / f"{date.month:02d}"
                else:
                    target = self.path / str(date.year) / f"{date.month:02d}" / f"{date.day:02d}"

                if filepath.parent != target:
                    if not self.dry_run:
                        target.mkdir(parents=True, exist_ok=True)

                    target_path = target / filepath.name
                    counter = 1
                    while target_path.exists():
                        target_path = target / f"{filepath.stem}_{counter}{filepath.suffix}"
                        counter += 1

                    try:
                        if self.dry_run:
                            print(f"[DRY RUN] Would move: {filepath} → {target_path}")
                        else:
                            filepath.rename(target_path)
                            print(f"Moved: {filepath.name} → {target}")
                        self.stats['files_organized'] += 1
                    except Exception as e:
                        print(f"Error moving {filepath}: {e}")
                        self.stats['errors'] += 1

                self._report_progress()

    def remove_empty_folders(self):
        print("\n🧹 Removing empty folders...")
        for root, dirs, files in os.walk(self.path, topdown=False):
            if self._cancel_requested():
                return

            if root == str(self.path):
                continue

            try:
                contents = os.listdir(root)
                if not contents or contents == ['.DS_Store']:
                    if not self.dry_run:
                        for item in contents:
                            os.remove(os.path.join(root, item))
                        os.rmdir(root)
                    self.stats['empty_folders_removed'] += 1
            except Exception as e:
                print(f"Error removing folder {root}: {e}")
                self.stats['errors'] += 1

            self._report_progress()

    # --------------------------------------------------
    # Run
    # --------------------------------------------------
    def run(self):
        self.start_time = time.time()

        self.total_steps = sum(
            1 for p in self.path.rglob('*')
            if p.is_file() and p.suffix.lower() in self.media_extensions
        )

        if self.total_steps == 0:
            print("No media files found.")
            return

        duplicates = []
        if self.should_remove_duplicates:
            duplicates = self.find_duplicates()
            self.remove_duplicates(duplicates)

        self.organize_files()
        self.remove_empty_folders()

        print("\n✅ Done.")

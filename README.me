# 📸 Media File Organizer & Duplicate Remover

A powerful Python script to organize your photo and video collections by date and remove duplicate files. Perfect for cleaning up messy media libraries!

## ✨ Features

- **🔍 Duplicate Detection**: Find and remove duplicate photos/videos based on:
  - SHA256 hash comparison (exact duplicates)
  - Filename matching

- **📅 Date-Based Organization**: Automatically organize files into folders by:
  - Year (e.g., `2024/`)
  - Year and Month (e.g., `2024/03/`)
  - Year, Month, and Day (e.g., `2024/03/15/`)

- **🗓️ Smart Date Extraction**: Gets dates from multiple sources:
  - EXIF metadata (photos)
  - Filename patterns (supports multiple formats)
  - File modification date (fallback)

- **🗂️ Empty Folder Cleanup**: Automatically removes:
  - Empty folders after organizing
  - Folders containing only `.DS_Store` files (macOS)

- **🎯 Interactive Menu**: Easy-to-use interface with options for:
  - Duplicate removal
  - Organization mode selection
  - Dry-run preview mode

- **📊 Detailed Statistics**: Shows:
  - Total files processed
  - Duplicates found and removed
  - Files organized
  - Empty folders removed
  - Space freed
  - Any errors encountered

## 🚀 Quick Start

### Prerequisites

- Python 3.6 or higher
- Pillow library (optional, for EXIF data reading)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/media-organizer.git
cd media-organizer
```

2. Install dependencies:
```bash
pip install Pillow
```

> **Note**: The script works without Pillow, but won't be able to read EXIF metadata from photos.

### Basic Usage

Run with interactive menu:
```bash
python media_organizer.py /path/to/your/photos
```

Or specify the path when prompted:
```bash
python media_organizer.py
```

## 📖 Usage Examples

### Interactive Mode (Recommended)
```bash
python media_organizer.py ~/Pictures/Vacation2024
```

The script will ask you:
1. Whether to remove duplicates
2. How to organize files (by year, month, day, or not at all)
3. Whether to run in dry-run mode (preview changes)

### Command-Line Mode

Skip the menu and run directly with options:

```bash
# Dry run - see what would happen without making changes
python media_organizer.py ~/Pictures --remove-duplicates --organize year_month --dry-run

# Remove duplicates only
python media_organizer.py ~/Pictures --no-menu --remove-duplicates

# Organize by year and month
python media_organizer.py ~/Pictures --no-menu --organize year_month

# Full cleanup: remove duplicates, organize by date, skip dry-run
python media_organizer.py ~/Pictures --no-menu --remove-duplicates --organize year_month_day
```

### Command-Line Options

| Option | Description |
|--------|-------------|
| `path` | Path to the folder to process |
| `--no-menu` | Skip interactive menu |
| `--remove-duplicates` | Remove duplicate files |
| `--organize {none,year,year_month,year_month_day}` | Organization mode |
| `--dry-run` | Preview changes without modifying files |

## 📁 Supported File Types

### Images
- `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.webp`, `.heic`

### Videos
- `.mp4`, `.avi`, `.mov`, `.mkv`, `.wmv`, `.flv`, `.webm`, `.m4v`

## 🔧 How It Works

### Duplicate Detection
1. Scans all media files in the folder and subfolders
2. Calculates SHA256 hash for each file
3. Compares hashes to find exact duplicates
4. Keeps the first occurrence, removes others

### Date Extraction Priority
1. **EXIF metadata** (for photos with Pillow installed)
2. **Filename patterns**: Recognizes formats like:
   - `YYYY-MM-DD` or `YYYY_MM_DD`
   - `YYYYMMDD`
   - `DD-MM-YYYY` or `DD_MM_YYYY`
   - `IMG_YYYYMMDD`
3. **File modification date** (fallback)

### Organization Process
1. Extracts date from each file
2. Creates target folder structure based on selected mode
3. Moves files to appropriate folders
4. Handles filename conflicts automatically (adds `_1`, `_2`, etc.)
5. Removes empty folders left behind

## 📊 Example Output

```
🎬 Starting Media Organizer
Path: /Users/alex/Pictures/Vacation2024
Remove duplicates: True
Organize by: year_month
Dry run: False

🔍 Scanning for duplicates...

🗑️  Removing 5 duplicate(s)...
Removed: /Users/alex/Pictures/Vacation2024/copy_IMG_1234.jpg
Removed: /Users/alex/Pictures/Vacation2024/IMG_1234 (1).jpg
...

📁 Organizing files by year_month...
Moved: IMG_1234.jpg -> 2024/03
Moved: VID_5678.mp4 -> 2024/03
...

🗂️  Removing empty folders...
Removed empty folder: /Users/alex/Pictures/Vacation2024/old_folder
✅ Total empty folders removed: 3

==================================================
📊 STATISTICS
==================================================
Total media files found:    150
Duplicates found:           5
Duplicates removed:         5
Files organized:            145
Empty folders removed:      3
Space freed:                125.45 MB
Errors encountered:         0
==================================================

✅ Complete!
```

## ⚠️ Important Notes

- **Always use `--dry-run` first** to preview changes before actually modifying your files
- **Backup your files** before running the script without dry-run mode
- The script preserves original files when organizing (moves, not copies)
- Duplicate detection is based on content hash, not just filename
- Empty folders are only removed after all operations complete

## 🛡️ Safety Features

- **Dry-run mode**: Preview all changes before execution
- **Confirmation prompt**: Asks for confirmation before making changes
- **Automatic conflict resolution**: Renames files if target already exists
- **Comprehensive error handling**: Continues processing even if individual files fail
- **Detailed logging**: Shows exactly what's being done

## 🐛 Troubleshooting

### "Pillow not installed" warning
Install Pillow to enable EXIF data reading:
```bash
pip install Pillow
```

### Permission errors
Make sure you have read/write permissions for the target folder:
```bash
chmod -R u+rw /path/to/folder
```

### Files not organizing by date
The script tries multiple methods to extract dates. If all fail, it uses the file modification date. Check that:
- Files have EXIF data (for photos)
- Filenames contain recognizable date patterns
- File modification dates are correct

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Uses [Pillow](https://python-pillow.org/) for EXIF data extraction
- Inspired by the need to organize thousands of vacation photos

## 📞 Support

If you encounter any issues or have questions, please [open an issue](https://github.com/yourusername/media-organizer/issues) on GitHub.

---

Made with ❤️ for photographers and digital hoarders everywhere!
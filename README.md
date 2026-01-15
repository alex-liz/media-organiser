# Media Organiser

Media Organiser is a lightweight tool to help you organise your photos, videos and other media files into a consistent directory structure based on metadata (timestamps, camera model, tags) and user-defined rules. It supports dry-runs, renaming, deduplication, tagging, and flexible output layouts so you can tame messy media dumps and build a clean, searchable library.

## Key features
- Organise by date, camera model, file type, or custom metadata
- Rename files using configurable patterns (e.g. `{YYYY}-{MM}-{DD}_{camera}_{seq}`)
- Dry-run mode to preview changes without modifying files
- Detect and handle duplicates (move, link, or skip)
- Preserve or normalise file timestamps and metadata
- Configurable file-handling rules and output layouts
- Batch processing and progress reporting
- Optional thumbnail generation and simple indexing

## Supported media types
- Photos: JPEG, PNG, HEIC (where supported), RAW formats (where supported)
- Videos: MP4, MOV, MKV, etc.
- Audio: MP3, WAV, FLAC (basic grouping/organising)
- Any other file types can be handled using extension-based rules

## Quickstart

1. Clone the repository
   ```bash
   git clone git@github.com:alex-liz/media-organiser.git
   cd media-organiser
   ```

2. Install dependencies and run
   - If this project uses Node (see repository files):  
     ```bash
     npm install
     npm run build
     npm start -- --source ./incoming --dest ./library
     ```
   - If this project uses Python (see repository files):  
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     pip install -r requirements.txt
     python -m media_organiser --source ./incoming --dest ./library
     ```
   - Or use Docker (if a Dockerfile is provided):
     ```bash
     docker build -t media-organiser .
     docker run --rm -v $(pwd)/incoming:/incoming -v $(pwd)/library:/library media-organiser --source /incoming --dest /library
     ```

Adjust the commands above to match the repository language and entrypoint.

## CLI usage (example)
Usage:
```
media-organiser [options] <source> <destination>
```

Common options:
- `--dry-run` — show what would happen without changing files
- `--pattern` — filename pattern, e.g. `"{YYYY}{MM}{DD}_{camera}_{seq}"`
- `--dedupe` — enable duplicate detection
- `--move` / `--copy` — whether to move or copy files
- `--threads` — concurrency for processing
- `--config <file>` — path to a YAML/JSON config file

Examples:
```bash
# Dry run to see proposed changes
media-organiser --dry-run ./incoming ./organized

# Rename and move into year/month/day folders
media-organiser --pattern "{YYYY}/{MM}/{DD}/{camera}/{filename}" ./incoming ./organized

# Move and dedupe
media-organiser --move --dedupe ./incoming ./organized
```

## Example config (YAML)
```yaml
# config.yml
pattern: "{YYYY}/{MM}/{DD}/{camera}/{seq}_{original}"
dedupe:
  strategy: checksum   # checksum | filename | timestamp
  action: skip         # skip | move-to-duplicates | link
preserve_timestamps: true
thumbnail:
  enabled: true
  size: 320
file_types:
  include:
    - jpg
    - jpeg
    - png
    - mp4
exclude_paths:
  - ".thumbnails"
log:
  level: info
  file: ./media-organiser.log
```

## Library layout recommendations
- Year/Month/Day structure for time-based organisation
- Camera/Device subfolders when keeping per-device grouping
- A `duplicates/` or `lost-and-found/` folder for files that can’t be confidently placed

Example:
```
library/
└── 2025/
    └── 01/
        └── 15/
            ├── iPhone12/
            │   ├── 2025-01-15_01.jpg
            │   └── ...
            └── GoPro/
                └── 2025-01-15_01.mp4
duplicates/
```

## Troubleshooting & tips
- Always run with `--dry-run` first to verify the results.
- Keep backups until you are confident your rules work.
- If metadata is missing or incorrect, the tool falls back to file timestamp; decide your fallback strategy in config.
- Large collections benefit from enabling concurrency/threads and incremental runs.

## Contributing
Contributions welcome! Please:
1. Open an issue to propose new features or report bugs.
2. Submit a PR for changes, include tests where relevant, and keep commits focused.
3. Document new options in this README.

## Tests
- If tests exist, run:
  ```bash
  npm test
  # or
  pytest
  ```
Add or update tests when changing behaviour.

## License
Specify the project license here (e.g. MIT). Add a LICENSE file at the repo root.

## Acknowledgements
- Tools and libraries used for metadata extraction, image/video handling, and checksum/dedup logic.
- Contributors and maintainers.

---

If you'd like, I can:
- Tailor installation and example commands to the repository's actual stack (Node, Python, Go, etc.) after you tell me which language/runtime is used.
- Add badges (CI, license, coverage) and a short description for the repository homepage.
- Generate a CONTRIBUTING.md and CODE_OF_CONDUCT.md next.

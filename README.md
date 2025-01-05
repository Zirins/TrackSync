# TrackSync - Playlist Merger and Organizer

## Overview
TrackSync is a Python-based tool designed to **merge and organize music files** from two folders while preserving **track order**, avoiding **duplicates**, and handling **renumbering** automatically. It is particularly useful for cases where playlists have been updated, and some tracks were **deleted or reordered**.

The tool prioritizes one folder (the **priority folder**) as the source for the **correct order** and fills in any gaps using files from the **secondary folder**.

---

## Features
- **Preserve Track Order**: Maintains numbering from the **priority folder** while integrating unmatched tracks from the **secondary folder**.
- **Avoid Duplicates**: Matches tracks based on **metadata** (title, artist) or **filename similarity** to prevent duplicates.
- **Unicode Support**: Handles filenames with **Chinese characters** and other **Unicode text**.
- **Dynamic Output Folder**: Creates the output folder in the **same directory as the priority folder**.
- **Renumber Tracks**: Ensures consistent filenames like `Track 001`, `Track 002`, etc.
- **Error Handling**: Skips files with **missing metadata** and logs warnings.
- **Non-Destructive**: Files are **copied**, not moved, leaving the original folders unchanged.

---

## Requirements
- Python 3.6 or later
- Required Libraries:
  ```bash
  pip install mutagen
  ```

---

## Usage
### 1. Run the Script
```bash
python tracksync.py
```

### 2. Provide Input Paths
Example:
```
Enter the path to the priority folder: "C:\Music\FavPlaylist1"
Enter the path to the secondary folder: "C:\Music\FavPlaylist2"
Enter the output folder name: unified
```

### 3. Output Folder
The output folder will be created **inside the priority folder's directory**:
```
E:\Music\unified
```

---

## How It Works
### 1. Load Metadata
- Extracts **track numbers**, **titles**, and **artists** from audio files using **`mutagen`**.
- Skips invalid or unreadable files.

### 2. Match Tracks
- Matches tracks based on **metadata similarity** and **filename comparisons**.
- Prioritizes the **priority folder** but fills gaps using the **secondary folder**.

### 3. Resolve Conflicts
- Renumbers tracks sequentially to resolve conflicts and ensure order consistency.

### 4. Copy and Renumber Files
- Copies matched and unmatched files into the **output folder** with new filenames (e.g., `Track 001 - Song.mp3`).

---

## Example Output
```
Loading priority folder...
Loading secondary folder...
Matching tracks and preserving priority order...
Renumbering and copying files to output folder...
Copied: Song A.mp3 -> Track 001 - Song A.mp3
Copied: Song B.mp3 -> Track 002 - Song B.mp3
Copied: Song C.mp3 -> Track 003 - Song C.mp3
Copied: New Song D.mp3 -> Track 004 - New Song D.mp3
Copied: New Song E.mp3 -> Track 005 - New Song E.mp3
Process completed successfully!

```

---

## Error Handling
- Logs warnings for **files missing metadata**.
- Replaces **invalid characters** in filenames (e.g., `?`, `*`) to avoid filesystem errors.
- Skips **unreadable files** but continues processing others.

---

## Limitations
- Matches based on **metadata similarity**, so files without metadata may not match correctly.
- Does not support **nested folders**—all tracks must be in the top-level directory.

---

## Future Features
- **Logs**: Add detailed log files for errors and actions taken.
- **Progress Bars**: Display status for long playlists.
- **GUI Support**: Build a visual interface using **`tkinter`** or **`PyQt5`**.
- **More Formats**: Expand to support **video files** or additional audio formats.

---

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to add.

---

## License
This project is licensed under the **MIT License**.

---

## Contact
For issues or questions, feel free to **open an issue** on the GitHub repository.

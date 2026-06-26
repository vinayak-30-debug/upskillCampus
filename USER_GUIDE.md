# File Organizer User Guide

## Start the App

Run:

```bash
python main.py
```

## Organize Files

1. Click **Browse** and select a folder.
2. Click **Preview** to see where files will be moved.
3. Click **Organize Files** to move files into category folders.

Files are moved into the selected output folder. By default, this is `Organized_Files`.

## Preferences

- **Output folder**: Change the parent folder where organized files are stored.
- **Include subfolders**: Also scan files inside subdirectories.
- **Custom Category**: Add your own category name and extensions.

Example:

- Name: `Design`
- Extensions: `.psd .ai .fig`

## Logs

Each organize operation writes details to:

```text
Organized_Files/organizer.log
```

The log includes timestamps, moved file paths, categories, and total files moved.

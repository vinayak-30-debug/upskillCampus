from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import shutil
from typing import Iterable


ORGANIZED_FOLDER = "Organized_Files"
DEFAULT_CATEGORY = "Others"

FILE_CATEGORIES: dict[str, set[str]] = {
    "Images": {
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".webp",
        ".svg",
        ".ico",
        ".heic",
        ".tiff",
    },
    "Documents": {
        ".pdf",
        ".doc",
        ".docx",
        ".txt",
        ".rtf",
        ".odt",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
        ".csv",
        ".json",
        ".xml",
        ".md",
    },
    "Videos": {
        ".mp4",
        ".mkv",
        ".mov",
        ".avi",
        ".wmv",
        ".flv",
        ".webm",
    },
    "Audio": {
        ".mp3",
        ".wav",
        ".aac",
        ".flac",
        ".ogg",
        ".m4a",
        ".wma",
    },
    "Archives": {
        ".zip",
        ".rar",
        ".7z",
        ".tar",
        ".gz",
        ".bz2",
    },
    "Code": {
        ".py",
        ".java",
        ".c",
        ".cpp",
        ".cs",
        ".js",
        ".ts",
        ".html",
        ".css",
        ".php",
        ".sql",
    },
    "Applications": {
        ".exe",
        ".msi",
        ".bat",
        ".cmd",
        ".apk",
    },
    "Fonts": {
        ".ttf",
        ".otf",
        ".woff",
        ".woff2",
    },
}


@dataclass(frozen=True)
class MoveResult:
    source: Path
    destination: Path
    category: str


def normalize_extensions(extensions: Iterable[str]) -> set[str]:
    normalized: set[str] = set()
    for extension in extensions:
        clean_extension = extension.strip().lower()
        if not clean_extension:
            continue
        if not clean_extension.startswith("."):
            clean_extension = f".{clean_extension}"
        normalized.add(clean_extension)
    return normalized


def sanitize_category_name(category: str) -> str:
    safe_name = "".join(
        character if character.isalnum() or character in (" ", "-", "_") else "_"
        for character in category.strip()
    )
    return safe_name or DEFAULT_CATEGORY


def normalize_custom_categories(
    custom_categories: dict[str, Iterable[str]] | None,
) -> dict[str, set[str]]:
    if not custom_categories:
        return {}

    normalized: dict[str, set[str]] = {}
    used_extensions: set[str] = set()

    for category, extensions in custom_categories.items():
        safe_category = sanitize_category_name(category)
        clean_extensions = normalize_extensions(extensions)
        clean_extensions -= used_extensions
        if not clean_extensions:
            continue

        normalized[safe_category] = clean_extensions
        used_extensions.update(clean_extensions)

    return normalized


def get_category(
    file_path: Path,
    custom_categories: dict[str, Iterable[str]] | None = None,
) -> str:
    """Return the folder category for a file based on its extension."""
    extension = file_path.suffix.lower()

    for category, extensions in normalize_custom_categories(custom_categories).items():
        if extension in extensions:
            return category

    for category, extensions in FILE_CATEGORIES.items():
        if extension in extensions:
            return category

    return DEFAULT_CATEGORY


def unique_destination(destination: Path) -> Path:
    """Avoid overwriting files by adding a number to duplicate names."""
    if not destination.exists():
        return destination

    parent = destination.parent
    stem = destination.stem
    suffix = destination.suffix
    counter = 1

    while True:
        candidate = parent / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def validate_directory(directory: str | Path) -> Path:
    target_dir = Path(directory).expanduser().resolve()

    if not target_dir.exists():
        raise FileNotFoundError(f"Directory does not exist: {target_dir}")
    if not target_dir.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {target_dir}")

    return target_dir


def iter_organizable_files(
    target_dir: Path,
    organized_root: Path,
    recursive: bool = False,
) -> Iterable[Path]:
    candidates = target_dir.rglob("*") if recursive else target_dir.iterdir()

    for item in candidates:
        if not item.is_file():
            continue
        if item.is_relative_to(organized_root):
            continue
        yield item


def scan_directory(
    directory: str | Path,
    custom_categories: dict[str, Iterable[str]] | None = None,
    output_folder: str = ORGANIZED_FOLDER,
    recursive: bool = False,
) -> list[MoveResult]:
    """Return the files that can be organized without moving them."""
    target_dir = validate_directory(directory)
    organized_root = target_dir / sanitize_category_name(output_folder)
    planned_files: list[MoveResult] = []

    for item in iter_organizable_files(target_dir, organized_root, recursive):
        category = get_category(item, custom_categories)
        destination = unique_destination(organized_root / category / item.name)
        planned_files.append(MoveResult(item, destination, category))

    return planned_files


def organize_directory(
    directory: str | Path,
    custom_categories: dict[str, Iterable[str]] | None = None,
    output_folder: str = ORGANIZED_FOLDER,
    recursive: bool = False,
    enable_logging: bool = True,
) -> list[MoveResult]:
    """Organize files into an Organized_Files folder with category subfolders."""
    target_dir = validate_directory(directory)
    organized_root = target_dir / sanitize_category_name(output_folder)
    moved_files: list[MoveResult] = []

    for item in iter_organizable_files(target_dir, organized_root, recursive):
        category = get_category(item, custom_categories)
        category_folder = organized_root / category
        category_folder.mkdir(parents=True, exist_ok=True)

        destination = unique_destination(category_folder / item.name)
        shutil.move(str(item), str(destination))
        moved_files.append(MoveResult(item, destination, category))

    if enable_logging:
        write_operation_log(organized_root, moved_files)

    return moved_files


def write_operation_log(organized_root: Path, moved_files: list[MoveResult]) -> None:
    organized_root.mkdir(parents=True, exist_ok=True)
    log_file = organized_root / "organizer.log"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with log_file.open("a", encoding="utf-8") as file:
        file.write(f"[{timestamp}] Operation started\n")
        if not moved_files:
            file.write("No files moved.\n")
        for result in moved_files:
            file.write(
                f"{result.source} -> {result.destination} ({result.category})\n"
            )
        file.write(f"Total files moved: {len(moved_files)}\n\n")

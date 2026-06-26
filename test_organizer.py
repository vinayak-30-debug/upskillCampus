from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from organizer import organize_directory, scan_directory


class OrganizerTests(unittest.TestCase):
    def test_organizes_known_and_unknown_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "image.jpg").write_text("image", encoding="utf-8")
            (root / "notes.unknown").write_text("other", encoding="utf-8")

            moved = organize_directory(root, enable_logging=False)
            destinations = {result.destination.relative_to(root) for result in moved}

            self.assertIn(Path("Organized_Files/Images/image.jpg"), destinations)
            self.assertIn(Path("Organized_Files/Others/notes.unknown"), destinations)

    def test_custom_category_has_priority(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "mock.dat").write_text("data", encoding="utf-8")

            preview = scan_directory(root, {"Data": [".dat"]})

            self.assertEqual(preview[0].category, "Data")

    def test_duplicate_names_are_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            existing = root / "Organized_Files" / "Documents"
            existing.mkdir(parents=True)
            (existing / "report.pdf").write_text("old", encoding="utf-8")
            (root / "report.pdf").write_text("new", encoding="utf-8")

            moved = organize_directory(root, enable_logging=False)

            self.assertEqual(moved[0].destination.name, "report_1.pdf")


if __name__ == "__main__":
    unittest.main()

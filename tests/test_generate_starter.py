import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1]
GENERATOR = SOURCE / "scripts" / "generate_starter.py"


class GenerateStarterTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)

    def generate(self, destination, name="Pocket Arcade"):
        return subprocess.run(
            [sys.executable, str(GENERATOR), "--name", name, str(destination)],
            capture_output=True,
            text=True,
            cwd=self.directory,
        )

    def test_new_project_is_independent_and_source_unchanged(self):
        source_project = SOURCE / "godot" / "project.godot"
        original = hashlib.sha256(source_project.read_bytes()).hexdigest()
        destination = self.directory / "my game"
        result = self.generate(destination)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(original, hashlib.sha256(source_project.read_bytes()).hexdigest())
        project = (destination / "godot" / "project.godot").read_text()
        self.assertIn('config/name="Pocket Arcade"', project)
        self.assertNotIn(str(SOURCE), (destination / "README.md").read_text())
        self.assertTrue((destination / "godot" / "scenes" / "Main.tscn").is_file())
        self.assertTrue((destination / "godot" / "export_presets.cfg").is_file())
        self.assertTrue((destination / "rust" / "my_ext.gdextension").is_file())
        makefile = (destination / "Makefile").read_text()
        self.assertIn("ci: smoke fixtures input-tests export-web", makefile)
        self.assertNotIn("generator-tests:", makefile)
        self.assertNotIn("scripts/generate_starter.py", makefile)
        self.assertFalse((destination / "godot" / "addons").exists())
        self.assertFalse((destination / ".git").exists())
        self.assertFalse((destination / "godot" / ".godot").exists())
        self.assertFalse(any(path.is_symlink() for path in destination.rglob("*")))
        provenance = json.loads((destination / "source-provenance.json").read_text())
        self.assertEqual(provenance["base_commit"], subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=SOURCE, text=True).strip())
        self.assertTrue(provenance["dirty_source"])
        self.assertIn("dirty_source", (destination / "README.md").read_text())

    def test_existing_destination_refused_without_mutation(self):
        destination = self.directory / "exists"
        destination.mkdir()
        sentinel = destination / "keep"
        sentinel.write_text("untouched")
        result = self.generate(destination)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(sentinel.read_text(), "untouched")

    def test_invalid_name_and_path_refused(self):
        for name in ("", "../escape", 'bad"name', "../", "."):
            with self.subTest(name=name):
                destination = self.directory / "new"
                result = self.generate(destination, name)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(destination.exists())
        result = self.generate(SOURCE / "nested")
        self.assertNotEqual(result.returncode, 0)

    def test_private_and_build_names_are_filtered(self):
        spec = importlib.util.spec_from_file_location("starter_generator", GENERATOR)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        names = [".git", ".godot", "target", "addons", "evidence", ".env.local", "credentials.json", "secret.pem", "private.p8", "build", "Main.tscn"]
        ignored = module.ignore_files(SOURCE / "godot", names)
        self.assertEqual(ignored, set(names) - {"Main.tscn"})

    def test_cache_artifacts_are_not_copied(self):
        destination = self.directory / "new"
        result = self.generate(destination)
        self.assertEqual(result.returncode, 0, result.stderr)
        for path in destination.rglob("*"):
            self.assertNotIn(path.name, {".godot", ".git", "__pycache__", ".env", "evidence", "target", "bin", "site", ".secrets"})
            self.assertNotIn(path.suffix, {".so", ".dylib", ".dll", ".pyc"})


if __name__ == "__main__":
    unittest.main()

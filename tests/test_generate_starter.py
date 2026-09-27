import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


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
        for unsupported in ("generator-tests:", "docs-build:", "dev-ci:", "ci-local:", "ensure-uv:", "scripts/generate_starter.py", "include runtime.mk"):
            self.assertNotIn(unsupported, makefile)
        self.assertEqual(makefile, (SOURCE / "runtime.mk").read_text())
        for prerequisite in ("godot/project.godot", "godot/export_presets.cfg", "godot/scripts/smoke_test.gd", "godot/scripts/run_fixtures.gd", "godot/scripts/run_input_tests.gd", "rust/Cargo.toml", "rust/my_ext.gdextension"):
            self.assertTrue((destination / prerequisite).is_file(), prerequisite)
        for target in ("ci", "gdscript-ci", "export-web", "serve-web"):
            self.assertEqual(subprocess.run(["make", "-n", target], cwd=destination, capture_output=True).returncode, 0, target)
        self.assertFalse((destination / "godot" / "addons").exists())
        self.assertFalse((destination / ".git").exists())
        self.assertFalse((destination / "godot" / ".godot").exists())
        self.assertFalse(any(path.is_symlink() for path in destination.rglob("*")))
        provenance = json.loads((destination / "source-provenance.json").read_text())
        self.assertEqual(provenance["base_commit"], subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=SOURCE, text=True).strip())
        actual_dirty = bool(subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=all"], cwd=SOURCE))
        self.assertEqual(provenance["dirty_source"], actual_dirty)
        self.assertIn(f"dirty_source: {str(actual_dirty).lower()}", (destination / "README.md").read_text())

    def test_clean_and_dirty_source_provenance_in_isolated_repositories(self):
        spec = importlib.util.spec_from_file_location("starter_generator", GENERATOR)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        source = self.directory / "fixture-source"
        source.mkdir()
        for directory in ("godot", "rust"):
            shutil.copytree(SOURCE / directory, source / directory, ignore=module.ignore_files)
        shutil.copy2(SOURCE / "runtime.mk", source / "runtime.mk")
        shutil.copy2(SOURCE / ".gitignore", source / ".gitignore")
        subprocess.run(["git", "init", "-q", str(source)], check=True)
        subprocess.run(["git", "-C", str(source), "add", "."], check=True)
        subprocess.run(["git", "-C", str(source), "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "Fixture"], check=True)
        commit = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
        with patch.object(module, "SOURCE", source):
            clean = self.directory / "clean"
            module.generate(clean, "Clean Starter")
            self.assertEqual(json.loads((clean / "source-provenance.json").read_text()), {"base_commit": commit, "dirty_source": False})
            (source / "godot" / "project.godot").write_text((source / "godot" / "project.godot").read_text() + "\n")
            dirty = self.directory / "dirty"
            module.generate(dirty, "Dirty Starter")
            self.assertEqual(json.loads((dirty / "source-provenance.json").read_text()), {"base_commit": commit, "dirty_source": True})
            self.assertIn("dirty_source: true", (dirty / "README.md").read_text())

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

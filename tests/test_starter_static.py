"""Source checkout and generated profile boundaries."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ProfileBoundaryTests(unittest.TestCase):
    def test_clean_native_checkout_has_no_installed_extension(self):
        self.assertEqual(list((ROOT / "godot").rglob("*.gdextension")), [])
        self.assertTrue((ROOT / "rust/my_ext.gdextension").is_file())
        self.assertNotIn("RustSmoke", (ROOT / "godot/scripts/smoke_test.gd").read_text())
        self.assertNotIn("export-web", (ROOT / "runtime.mk").read_text())
        self.assertIn("ci: generator-tests", (ROOT / "Makefile").read_text())

    def test_web_profile_has_extension_free_export(self):
        project = (ROOT / "profiles/web-mobile/project.godot").read_text()
        preset = (ROOT / "godot/export_presets.cfg").read_text()
        runtime = (ROOT / "profiles/web-mobile/Makefile").read_text()
        self.assertIn('renderer/rendering_method="gl_compatibility"', project)
        self.assertIn('platform="Web"', preset)
        self.assertIn("variant/thread_support=false", preset)
        self.assertIn("variant/extensions_support=false", preset)
        self.assertIn("ci: smoke fixtures input-tests export-web", runtime)
        self.assertNotIn("native-smoke", runtime)

    def test_native_rust_cold_import_mitigation_preserves_required_checks(self):
        rust = (ROOT / "profiles/native-rust/Makefile").read_text()
        web = (ROOT / "profiles/web-mobile/Makefile").read_text()
        native = (ROOT / "runtime.mk").read_text()
        workflow = (ROOT / ".github/workflows/ci.yml").read_text()
        self.assertIn("import:\n\t$(GODOT) --headless --import --path godot --quit --frame-delay 800", rust)
        self.assertNotIn("--frame-delay", native)
        self.assertNotIn("--frame-delay", web)
        self.assertIn("ci: fmt-check lint test native-negative native-smoke smoke fixtures", rust)
        self.assertIn('make -C "$RUNNER_TEMP/rust-starter" ci', workflow)
        self.assertIn("for attempt in 1 2 3; do", workflow)
        self.assertIn("grep -Fq '[NATIVE SMOKE OK]'", workflow)
        self.assertIn("grep -Fq '[FIXTURES OK] 3 passed'", workflow)
        self.assertNotIn("continue-on-error", workflow)

    def test_ci_local_selects_web_workflow_job(self):
        makefile = (ROOT / "Makefile").read_text()
        workflow = (ROOT / ".github/workflows/ci.yml").read_text()
        local_target = makefile.split("ci-local:", 1)[1].split("ci-clean:", 1)[0]
        selected = re.search(r"(?m)^\s+-j ([\w-]+) \\$", local_target)
        self.assertIsNotNone(selected)
        self.assertIn(f"  {selected.group(1)}:", workflow)
        self.assertIn("  native-rust:", workflow)
        self.assertNotIn("workflow_dispatch' && inputs.native_rust", workflow)


if __name__ == "__main__":
    unittest.main()

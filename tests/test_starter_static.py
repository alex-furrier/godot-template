"""Cheap checks that guard default Web import from a native extension."""

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class WebDefaultTests(unittest.TestCase):
    def test_default_import_has_no_native_extension_descriptor(self):
        self.assertEqual(list((ROOT / "godot").rglob("*.gdextension")), [])
        self.assertTrue((ROOT / "rust" / "my_ext.gdextension").is_file())
        extension_list = ROOT / "godot" / ".godot" / "extension_list.cfg"
        if extension_list.exists():
            self.assertNotIn("res://addons/", extension_list.read_text())
        self.assertNotIn("RustSmoke", (ROOT / "godot" / "scripts" / "smoke_test.gd").read_text())

    def test_web_settings_and_build_do_not_require_rust(self):
        project = (ROOT / "godot" / "project.godot").read_text()
        preset = (ROOT / "godot" / "export_presets.cfg").read_text()
        makefile = (ROOT / "Makefile").read_text()
        self.assertIn('renderer/rendering_method="gl_compatibility"', project)
        self.assertIn('platform="Web"', preset)
        self.assertIn("variant/thread_support=false", preset)
        self.assertIn("variant/extensions_support=false", preset)
        runtime = (ROOT / "runtime.mk").read_text()
        self.assertIn("include runtime.mk", makefile)
        self.assertIn("ci: generator-tests", makefile)
        self.assertIn("ci: smoke fixtures input-tests export-web", runtime)
        self.assertIn("native-smoke: copy-ext import", runtime)
        self.assertNotIn("export_presets.cfg\n", (ROOT / ".gitignore").read_text())

    def test_ci_local_selects_a_real_web_workflow_job(self):
        makefile = (ROOT / "Makefile").read_text()
        workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text()
        local_target = re.search(r"(?ms)^ci-local:.*?(?=^[\w-]+:|\Z)", makefile)
        self.assertIsNotNone(local_target)
        selected = re.search(r"(?m)^\s+-j ([\w-]+) \\$", local_target.group())
        self.assertIsNotNone(selected)
        jobs = workflow.split("\njobs:\n", 1)[1]
        job_names = re.findall(r"(?m)^  ([\w-]+):\s*$", jobs)
        self.assertEqual(selected.group(1), "web")
        self.assertIn(selected.group(1), job_names)


if __name__ == "__main__":
    unittest.main()

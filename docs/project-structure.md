# Project structure

- `godot/core/` and `godot/tests/fixtures/`: shared typed state, event/tick API and deterministic fixtures.
- `godot/project.godot`, `godot/scenes/Main.tscn`, `godot/scripts/Main.gd`: native GDScript checkout project and minimal native scene.
- `godot/adapters/`: shared input, event and view adapter examples; Web movement uses `input_adapter.gd`.
- `profiles/web-mobile/`: portrait project settings, demo script, input test and Web runtime Makefile; `godot/export_presets.cfg` supplies the Web preset.
- `profiles/native-rust/`: Linux x86_64 runtime Makefile and extension descriptor installed only after build; `rust/` supplies native-only source.
- `scripts/generate_starter.py`: validates a new destination, copies shared sources and profile-owned files, and records profile/version/commit/dirty provenance.

Generated projects have their own Makefile and no runtime link to this checkout. No profile duplicates the shared core; add actual game rules to your generated consumer. [Verification](verification.md) separates automated checks from browser and physical-device proof.

# Project structure

- `godot/project.godot`: Compatibility renderer, portrait viewport and movement actions.
- `godot/scenes/Main.tscn` and `godot/scripts/Main.gd`: playable demo, drawing, start/pause/restart and 60 Hz simulation.
- `godot/adapters/input_adapter.gd`: keyboard/joystick movement and release.
- `godot/core/`: typed state, existing deterministic tick example and event adapter.
- `godot/tests/fixtures/`: JSON step fixtures; `godot/scripts/run_input_tests.gd`: focused input/lifecycle assertions.
- `godot/export_presets.cfg`: single-threaded extension-free Web export.
- `scripts/generate_starter.py`: refuses existing destinations and creates independent consumers.
- `rust/`: optional native Rust example; `rust/my_ext.gdextension` remains outside the Godot tree until `make native-smoke` installs it.

The consumer receives a copy of the maintained Godot starter, not a symlink or a runtime dependency on this checkout. Add game-specific logic and art in that consumer. [Verification](verification.md) records what has actually run.

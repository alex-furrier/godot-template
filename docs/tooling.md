# Tooling and local checks

The default path needs Godot 4.5.1, its matching Web export templates and uv (for template generator tests). Docker and Rust are optional. The generated consumer's `make ci` does not require uv because it does not ship the generator tests.

| Command | Effect |
| --- | --- |
| `make ci` | Generator tests, Godot smoke, JSON fixtures, input/lifecycle tests, Web export. |
| `make gdscript-ci` | Godot import, smoke, fixtures and input checks; no Web export templates needed. |
| `make export-web` | Export `build/web/index.html` with the single-threaded Web preset. |
| `make serve-web WEB_PORT=8000` | Serve the exported directory on localhost. |
| `make generator-tests` | Run Python generator safety tests; template only. |
| `make native-smoke` | Opt-in Linux Rust build, install extension and test it; not a Web check. |
| `make dev-ci` | Run `make ci` in the optional Docker container. |

Source files under `godot/core/` use typed Resources with a fixture runner. `godot/scripts/run_input_tests.gd` exercises keyboard/joystick normalization and lifecycle release. Headless checks do **not** prove actual canvas visuals or physical iPhone behavior. See [verification](verification.md) for evidence and gaps.

If you opt into the native Rust path, install Rust and run `make fmt`, `make lint`, `make test`, then `make native-smoke`. This creates `godot/addons/my_ext/my_ext.gdextension` locally. Use a fresh source tree to prove an extension-free default Web import/export; do not infer that the native library runs in Web.

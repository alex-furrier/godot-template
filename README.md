# Godot starter: native GDScript, native Rust, or Web/mobile

This Godot 4.5.1 template opens as a **native GDScript** project. Its small native scene advances a typed tick when you hold D/Right; `godot/core/` contains the shared typed state, events and three deterministic JSON fixtures. No Rust, Docker or Web export templates are needed to run this checkout.

```bash
make ci                 # native import, smoke, fixtures; generator tests require uv
```

To create a separate project, choose one of three runtime profiles. The established no-flag generator invocation still selects `web-mobile`, even though the source checkout opens native-first:

```bash
uv run --no-sync python scripts/generate_starter.py --name "My Game" --profile native-gdscript /absolute/path/to/new-native
uv run --no-sync python scripts/generate_starter.py --name "My Rust Game" --profile native-rust /absolute/path/to/new-rust
uv run --no-sync python scripts/generate_starter.py --name "My Web Game" /absolute/path/to/new-web
```

Each destination must be new and outside this checkout. In each generated directory, `make ci` uses **that profile's own Makefile**:

| Profile | `make ci` requires | What it does |
| --- | --- | --- |
| `native-gdscript` | Godot 4.5.1 | Import, smoke and fixtures; no export templates or Rust. |
| `native-rust` | Linux x86_64, Godot 4.5.1, Rust with rustfmt/clippy | fmt, clippy, core tests, negative missing-extension probe, extension build/install, mandatory RustSmoke and fixtures. Other native platforms are unverified. |
| `web-mobile` (no-flag default) | Godot 4.5.1, matching Web export templates | Import, smoke, fixtures, input tests and extension-free single-threaded Web export. `make serve-web` then serves `http://127.0.0.1:8000`. |

The Web demo uses a portrait Compatibility canvas: Enter/Space or START begins play, WASD/arrows or touch joystick move, P/Escape pauses, and R restarts. The demo is not a finished game. Rust is not supported in the Web profile. The Linux extension descriptor is installed **only** after the native Rust library builds; a clean generated native or Web project has no installed extension. Consumer projects exclude `.git`, caches, binaries, private files and template docs/tooling; they have no runtime dependency on this checkout. `source-provenance.json` records the chosen profile, Godot version, source commit and dirty flag. A dirty source cannot be reproduced from its commit alone. The generator does not initialize Git or migrate existing games: generate a new neighbor and port game rules deliberately.

Read [architecture](docs/architecture.md), [tooling](docs/tooling.md), [Rust guide](docs/rust-gdext.md) and [verification](docs/verification.md) for boundaries and evidence. No public hosting or physical-device acceptance is claimed. The separate documentation workflow can publish on pushes to main; the commands above do not deploy.

# Godot Web starter

This project starts with a portrait 2D GDScript demo that imports and exports to Web without building or loading Rust. Godot 4.5.1 and matching export templates are required. The default renderer is Compatibility, with a single-threaded Web preset.

Run `make ci` from the repository root, then `make serve-web` and open `http://127.0.0.1:8000`. See [getting started](getting-started.md) for controls and prerequisites, [verification](verification.md) for actual test evidence, and [tooling](tooling.md) for commands.

The existing typed `CoreAPI.step` and JSON fixtures are a small tick example, not a complete game or a promise of deterministic Godot physics. See [architecture](architecture.md) for the seam. The [Rust guide](rust-gdext.md) describes an optional **native-only** extension; it is never required by Web exports.

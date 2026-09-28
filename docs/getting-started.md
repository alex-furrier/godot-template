# Getting started

Install Godot 4.5.1. The source checkout is native GDScript: `make smoke fixtures` imports and checks the typed core without Rust, Docker or Web templates. `make ci` also runs generator tests and needs `uv`.

Generate a fresh independent project (an existing destination is refused):

```bash
uv run --no-sync python scripts/generate_starter.py --name "Native Game" --profile native-gdscript /absolute/path/to/new-native
cd /absolute/path/to/new-native
make ci
```

For browser/touch, use `--profile web-mobile` (or omit `--profile` for backwards compatibility). Its `make ci` needs matching Web export templates; `make serve-web` serves the exported canvas on localhost. For Linux x86_64 Rust, use `--profile native-rust`; its `make ci` needs cargo/rustfmt/clippy and asserts extension registration. These are distinct new outputs, not an in-place migration. Read [tooling](tooling.md) and [verification](verification.md) before claiming browser or device acceptance.

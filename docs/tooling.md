# Tooling and local checks

Godot 4.5.1 is required. The source checkout is native GDScript; its `make ci` runs Godot smoke and fixtures plus `uv`-backed generator tests. `make smoke fixtures` needs only Godot. Generated projects have their own Makefile and need no uv or template checkout.

| Generated profile | Command | Dependencies and result |
| --- | --- | --- |
| `native-gdscript` | `make ci` | Godot only: import, smoke and three fixtures. |
| `native-rust` | `make ci` | Linux x86_64 Godot and Rust: fmt check, clippy, core tests, missing-extension negative, extension build/install, mandatory RustSmoke, smoke and fixtures. |
| `web-mobile` | `make ci` | Godot and matching Web templates: smoke, fixtures, input lifecycle tests, extension-free Web export. |
| `web-mobile` | `make serve-web` | After export, serve `build/web/` on localhost. |

`make generator-tests` belongs to the source checkout. `make dev-ci` and `make ci-local` are optional container/act helpers, not requirements for native GDScript consumers; `ci-local` selects the Web CI job only. The separate Linux Rust CI job is required on pull requests, not a manual-only workflow. Headless smoke/export do not establish canvas interaction or physical-device behavior. Read [verification](verification.md).

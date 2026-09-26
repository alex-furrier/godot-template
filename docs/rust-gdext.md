# Optional native Rust extension

Web exports are GDScript-only by default. The Rust workspace at `rust/` is an optional **Linux native** example, not a dependency of `make ci` or an implementation of browser gameplay. No Rust Web export support is asserted.

`rust/core` contains pure Rust logic and unit tests; `rust/gdext_bridge` exposes the `RustSmoke` class. Run `make test` to test the Rust core, or `make fmt` and `make lint` for Rust checks. After installing a local Rust toolchain, `make native-smoke` builds the Linux shared library, copies `rust/my_ext.gdextension` into `godot/addons/my_ext/`, imports Godot and tests `RustSmoke` methods.

Godot scans `.gdextension` descriptors during import. The source project deliberately keeps the descriptor **outside** `godot/` until `make native-smoke` installs it, so a clean Web import never even attempts to load the missing native library. Do not run native-smoke before measuring default Web behavior in that same checkout. For a repeatable Web check after native work, use a fresh independent generated project; its generator excludes `addons/` and native binaries.

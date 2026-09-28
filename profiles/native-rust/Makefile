# Linux native Rust profile; requires Godot 4.5.1 and a Rust toolchain.
.PHONY: fmt-check lint test build-ext copy-ext native-smoke native-negative import smoke fixtures ci check
GODOT ?= godot
EXT_LIB := rust/target/debug/libmy_ext.so
EXT_DEST := godot/addons/my_ext/bin/linux/debug/libmy_ext.so

fmt-check:
	cd rust && cargo fmt --all --check
lint:
	cd rust && cargo clippy --workspace --all-targets -- -D warnings
test:
	cd rust && cargo test -p core
build-ext:
	cd rust && cargo build -p my_ext
copy-ext: build-ext
	@mkdir -p $(dir $(EXT_DEST))
	@cp $(EXT_LIB) $(EXT_DEST)
	@cp rust/my_ext.gdextension godot/addons/my_ext/my_ext.gdextension
import:
	$(GODOT) --headless --import --path godot --quit
smoke: import
	$(GODOT) --headless --path godot --script res://scripts/smoke_test.gd
fixtures: import
	$(GODOT) --headless --path godot --script res://scripts/run_fixtures.gd
native-smoke: copy-ext import
	$(GODOT) --headless --path godot --script res://scripts/native_smoke_test.gd
# The same mandatory registration probe must fail before the extension is installed.
native-negative:
	@test ! -e godot/addons/my_ext/my_ext.gdextension && test ! -e $(EXT_DEST)
	@log=$$(mktemp); trap 'rm -f "$$log"' EXIT; \
	if $(GODOT) --headless --path godot --script res://scripts/native_smoke_test.gd >"$$log" 2>&1; then \
		cat "$$log"; echo 'Missing extension unexpectedly passed'; exit 1; \
	fi; \
	cat "$$log"; grep -q '\[NATIVE SMOKE FAIL\] RustSmoke is not registered' "$$log"
ci: fmt-check lint test native-negative native-smoke smoke fixtures
check: ci

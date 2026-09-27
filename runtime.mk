# Shared Godot runtime commands for the template and generated games.
.PHONY: fmt lint test build-ext copy-ext native-smoke smoke ci check fixtures input-tests gdscript-ci export-web serve-web import

GODOT ?= godot
RUST_DIR := rust
EXT_NAME := my_ext
EXT_LIB_DEBUG := $(RUST_DIR)/target/debug/lib$(EXT_NAME).so
EXT_DEST_DEBUG := godot/addons/$(EXT_NAME)/bin/linux/debug/lib$(EXT_NAME).so

# Rust build + test
fmt:
	cd $(RUST_DIR) && cargo fmt --all

lint:
	cd $(RUST_DIR) && cargo clippy --workspace --all-targets -- -D warnings

test:
	cd $(RUST_DIR) && cargo test -p core

build-ext:
	cd $(RUST_DIR) && cargo build -p $(EXT_NAME)

# Opt-in native Linux extension. Never installed by default or by Web export.
copy-ext: build-ext
	@mkdir -p $(dir $(EXT_DEST_DEBUG))
	@cp $(EXT_LIB_DEBUG) $(EXT_DEST_DEBUG)
	@cp $(RUST_DIR)/my_ext.gdextension godot/addons/$(EXT_NAME)/my_ext.gdextension

native-smoke: copy-ext import
	$(GODOT) --headless --path godot --script res://scripts/native_smoke_test.gd

smoke: import
	$(GODOT) --headless --path godot --script res://scripts/smoke_test.gd

ci: smoke fixtures input-tests export-web

check: ci

# Import generates the global script class cache needed for class_name lookup.
import:
	$(GODOT) --headless --import --path godot --quit

fixtures: import
	$(GODOT) --headless --path godot --script res://scripts/run_fixtures.gd

input-tests: import
	$(GODOT) --headless --path godot --script res://scripts/run_input_tests.gd

gdscript-ci: smoke fixtures input-tests
	@echo "GDScript CI complete"

export-web: import
	@mkdir -p build/web
	$(GODOT) --headless --path godot --export-release Web $(abspath build/web/index.html)

WEB_PORT ?= 8000
serve-web:
	cd build/web && python3 -m http.server $(WEB_PORT) --bind 127.0.0.1

# Godot-only native GDScript starter. No Rust or Web export templates required.
.PHONY: import smoke fixtures ci check
GODOT ?= godot

import:
	$(GODOT) --headless --import --path godot --quit

smoke: import
	$(GODOT) --headless --path godot --script res://scripts/smoke_test.gd

fixtures: import
	$(GODOT) --headless --path godot --script res://scripts/run_fixtures.gd

ci: smoke fixtures

check: ci

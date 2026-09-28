# Shared Godot runtime commands for the template and generated games.
.PHONY: smoke ci check fixtures input-tests gdscript-ci export-web serve-web import

GODOT ?= godot

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

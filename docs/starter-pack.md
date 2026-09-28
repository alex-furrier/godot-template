# Extend a generated starter

Generate a new destination with `scripts/generate_starter.py --name "My Game" --profile native-gdscript /absolute/path/to/new-game` (run with `uv run --no-sync python` from the checkout). Choose `web-mobile` for the portrait touch demo; omit `--profile` to retain the original Web generator behavior. In the generated directory, `make ci` runs that profile's independent checks. Do not point generation at an existing game; port authored rules into the new neighbor instead.

The native scene advances the typed tick on D/Right. Web's `Main.gd` owns the bounded arena, lifecycle and movement, while `input_adapter.gd` combines normalized keyboard and one captured touch joystick. All profiles share the typed fixture core; put game-specific state and rules into your consumer. Browser canvas proof needs actual interaction and screenshot review; headless export is not physical-device acceptance. See [verification](verification.md).

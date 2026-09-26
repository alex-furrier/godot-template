# Architecture: a typed tick and a playable scene

The default starter has two distinct responsibilities. `godot/scripts/Main.gd` owns visible demo state (title, playing, paused), drawing, movement and start/pause/restart. Godot calls its `_physics_process(delta)` at the project's 60 Hz physics rate; movement speed uses that `delta`. Godot physics and browser frame timing are **not** claimed to be cross-platform deterministic.

`godot/core/core_api.gd` is a small typed **tick example**, not the whole game. `CoreAPI.step(GameState, GameInput)` copies its state, advances a generic integer tick and returns a `StepResult` containing state and a `TICK_ADVANCED` event. `step_dict()` converts JSON-shaped fixture data to Resources and back. The `decide()` and `generate()` methods are stubs; they do not implement AI or procedural content. The fixture runner in `godot/scripts/run_fixtures.gd` validates that narrow contract. For example:

```gdscript
var state := GameState.new()
var input := GameInput.new()
input.delta = 1
var result := CoreAPI.step(state, input)
# result.state.tick == 1; result.events contains TICK_ADVANCED
```

`godot/adapters/input_adapter.gd` reads `move_*` actions and one captured joystick touch. It limits keyboard/touch movement to unit length and clears the captured touch when released. `Main.gd` additionally releases pressed actions and pauses on focus loss. `run_input_tests.gd` exercises those boundaries and verifies movement occurs in playing state but not while paused.

For a new game, add its own rules/state under the generated project's `godot/` directory. Do not put collectibles/enemies into the template's generic `GameState`, or assume the Rust example is already wired to gameplay. The default import and Web export never require an extension descriptor. See [Rust](rust-gdext.md) for the separate native opt-in path and [verification](verification.md) for evidence.

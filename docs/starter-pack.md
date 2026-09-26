# Extend the playable starter

Open `godot/project.godot` in Godot 4.5.1 and run `Main.tscn`. The current demo already includes a bounded arena, a diamond controlled by WASD/arrows or a captured touch joystick, plus start, pause, resume and restart. Use it to test your game's first interactive loop before replacing it with authored game rules.

`godot/scripts/Main.gd` owns presentation and `_physics_process` at Godot's 60 Hz physics rate. It multiplies movement speed by physics `delta`, then clamps the character inside the visible arena. `godot/adapters/input_adapter.gd` combines keyboard and one captured touch, normalizes diagonal speed and releases it on touch-up or focus loss. The template's `GameState` records a generic fixture tick; keep game-specific fields in the generated game rather than adding them to that generic resource.

After changes, run `make gdscript-ci` for headless checks; `make export-web` and `make serve-web` for a browser build. A browser canvas needs actual keyboard/touch interaction and screenshot review before you claim it is usable on a phone. See [verification](verification.md).

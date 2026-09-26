# Getting started

Install Godot **4.5.1** and its matching Web export templates. Put the Godot executable on your PATH as `godot`. Install `uv` to run generator tests from the template; no Rust or Docker installation is needed for the default starter.

```bash
make ci
make serve-web
```

`make ci` imports the project, runs `[SMOKE OK]`, `[FIXTURES OK]` and `[INPUT OK]` checks, and exports `build/web/index.html`. Open `http://127.0.0.1:8000` rather than a `file://` URL. To run without Web templates, use `make gdscript-ci`; to use Docker, see [tooling](tooling.md).

The default demo starts paused on a title screen. Enter/Space or the touch START button begins play; WASD/arrows or the lower-left touch joystick move the diamond. P/Escape or PAUSE pauses; R restarts. Godot pauses and clears held input when the window loses focus.

Create a separate project with `uv run --no-sync python scripts/generate_starter.py --name "My Game" /absolute/path/to/new-game`; it refuses existing destinations. Read [verification](verification.md) before claiming exported-browser, iPhone or Android acceptance.

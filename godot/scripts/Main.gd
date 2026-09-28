extends Node2D

# Native checkout demo: the shared typed core stays independent of presentation.
var state: GameState

func _ready() -> void:
	state = GameState.new()
	queue_redraw()

func _physics_process(_delta: float) -> void:
	if Input.is_action_pressed("move_right"):
		state = CoreAPI.step(state, _tick_input()).state
		queue_redraw()

func _tick_input() -> GameInput:
	var tick := GameInput.new()
	tick.delta = 1
	return tick

func _draw() -> void:
	var font := ThemeDB.fallback_font
	draw_string(font, Vector2(42, 86), "GODOT NATIVE STARTER", HORIZONTAL_ALIGNMENT_LEFT, -1, 30)
	draw_string(font, Vector2(42, 132), "Hold D or Right to advance the typed tick", HORIZONTAL_ALIGNMENT_LEFT, -1, 18)
	draw_string(font, Vector2(42, 180), "Tick: %d" % state.tick, HORIZONTAL_ALIGNMENT_LEFT, -1, 24)

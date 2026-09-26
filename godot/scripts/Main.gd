extends Node2D

const SPEED := 220.0
const INK := Color("111827")
const PANEL := Color("1c2938")
const TEAL := Color("54dac5")
const GOLD := Color("f6cc70")
const TEXT := Color("f3f4ec")

var phase := "title"
var state: GameState
var player := Vector2.ZERO
var controls := InputAdapter.new()
var event_adapter := EventAdapter.new()


func _ready() -> void:
	reset_demo()
	get_viewport().size_changed.connect(queue_redraw)


func reset_demo() -> void:
	_stop_movement()
	state = GameState.new()
	state.rng_state = 42
	player = arena().get_center()
	phase = "title"
	_report_phase()
	queue_redraw()


func arena() -> Rect2:
	var size := get_viewport_rect().size
	var width: float = minf(390.0, size.x - 32.0)
	var top: float = minf(96.0, size.y * 0.22)
	return Rect2(Vector2((size.x - width) * 0.5, top), Vector2(width, maxf(80.0, size.y - top - 145.0)))


func joystick_center() -> Vector2:
	var bounds := arena()
	return Vector2(bounds.position.x + 74, get_viewport_rect().size.y - 82)


func action_button() -> Rect2:
	var bounds := arena()
	return Rect2(Vector2(bounds.end.x - 158, get_viewport_rect().size.y - 110), Vector2(142, 64))


func pause_button() -> Rect2:
	var bounds := arena()
	return Rect2(Vector2(bounds.end.x - 84, 18), Vector2(84, 52))


func _physics_process(delta: float) -> void:
	if phase != "playing":
		return
	var result := CoreAPI.step(state, _tick_input())
	state = result.state
	event_adapter.process_events(result.events, self)
	var bounds := arena().grow(-20)
	player += controls.movement() * SPEED * delta
	player = player.clamp(bounds.position, bounds.end)
	queue_redraw()


func _tick_input() -> GameInput:
	var tick := GameInput.new()
	tick.delta = 1
	return tick


func start_or_restart() -> void:
	if phase == "paused":
		phase = "playing"
		_stop_movement()
		_report_phase()
		queue_redraw()
	else:
		restart_demo()


func restart_demo() -> void:
	reset_demo()
	phase = "playing"
	_report_phase()
	queue_redraw()


func toggle_pause() -> void:
	if phase == "playing":
		phase = "paused"
	elif phase == "paused":
		phase = "playing"
	else:
		return
	_stop_movement()
	_report_phase()
	queue_redraw()


func _stop_movement() -> void:
	controls.clear()
	for action in ["move_left", "move_right", "move_up", "move_down"]:
		Input.action_release(action)


func _report_phase() -> void:
	# Browser console observation for lifecycle tests; the canvas still owns visual proof.
	print("[DEMO] phase=%s tick=%d player=%s" % [phase, state.tick, str(player)])


func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT or what == NOTIFICATION_WM_WINDOW_FOCUS_OUT:
		_stop_movement()
		if phase == "playing":
			phase = "paused"
			_report_phase()
		queue_redraw()


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_ENTER or event.keycode == KEY_SPACE:
			start_or_restart()
		elif event.keycode == KEY_ESCAPE or event.keycode == KEY_P:
			toggle_pause()
		elif event.keycode == KEY_R:
			restart_demo()
	elif event is InputEventScreenTouch:
		if event.pressed:
			if phase == "playing" and pause_button().has_point(event.position):
				toggle_pause()
			elif action_button().has_point(event.position):
				start_or_restart()
			elif phase == "playing":
				controls.touch_press(event.index, event.position, joystick_center())
		else:
			controls.touch_release(event.index)
		queue_redraw()
	elif event is InputEventScreenDrag:
		controls.touch_drag(event.index, event.position)
		queue_redraw()
	elif event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
		if phase == "playing" and pause_button().has_point(event.position):
			toggle_pause()
		elif action_button().has_point(event.position):
			start_or_restart()


func _draw() -> void:
	var size := get_viewport_rect().size
	draw_rect(Rect2(Vector2.ZERO, size), INK)
	var bounds := arena()
	draw_rect(bounds, PANEL)
	draw_rect(bounds.grow(-8), Color("23384a"), false, 2)
	var font := ThemeDB.fallback_font
	draw_string(font, Vector2(bounds.position.x + 4, 42), "POCKET ARCADE", HORIZONTAL_ALIGNMENT_LEFT, -1, 25, TEXT)
	draw_string(font, Vector2(bounds.position.x + 4, bounds.position.y - 9), "Move the diamond", HORIZONTAL_ALIGNMENT_LEFT, -1, 15, TEXT)
	draw_colored_polygon(PackedVector2Array([player + Vector2(0, -19), player + Vector2(19, 0), player + Vector2(0, 19), player + Vector2(-19, 0)]), TEAL)
	draw_circle(bounds.position + Vector2(bounds.size.x * 0.72, bounds.size.y * 0.35), 12, GOLD)
	if phase == "playing":
		_draw_button(pause_button(), "PAUSE")
	var stick := joystick_center()
	draw_arc(stick, 56, 0, TAU, 40, Color("778fa0"), 3)
	draw_circle(stick + controls.movement() * 28, 22, TEAL if controls.touch_index >= 0 else Color("607b87"))
	var label := "START" if phase == "title" else "RESUME" if phase == "paused" else "RESTART"
	_draw_button(action_button(), label)
	if phase != "playing":
		var message := "READY TO MOVE" if phase == "title" else "PAUSED"
		draw_rect(bounds.grow(-8), Color(0.07, 0.1, 0.15, 0.78))
		draw_string(font, bounds.get_center() + Vector2(-95, -10), message, HORIZONTAL_ALIGNMENT_LEFT, -1, 22, TEXT)
		draw_string(font, bounds.get_center() + Vector2(-118, 20), "WASD / ARROWS OR TOUCH", HORIZONTAL_ALIGNMENT_LEFT, -1, 15, TEXT)
		if phase == "paused":
			draw_string(font, bounds.get_center() + Vector2(-100, 47), "Press P to resume · R to restart", HORIZONTAL_ALIGNMENT_LEFT, -1, 13, TEXT)


func _draw_button(rect: Rect2, label: String) -> void:
	draw_rect(rect, TEAL)
	var font := ThemeDB.fallback_font
	var text_width := font.get_string_size(label, HORIZONTAL_ALIGNMENT_LEFT, -1, 19).x
	draw_string(font, Vector2(rect.get_center().x - text_width * 0.5, rect.get_center().y + 7), label, HORIZONTAL_ALIGNMENT_LEFT, -1, 19, INK)

extends SceneTree

func _initialize() -> void:
	if not ClassDB.class_exists("RustSmoke"):
		push_error("[NATIVE SMOKE FAIL] RustSmoke is not registered")
		quit(1)
		return
	var extension = ClassDB.instantiate("RustSmoke")
	if extension == null or extension.ping("hi") != "hi -> pong" or extension.calculate_damage(100, 1.5) != 150 or extension.greet_player("Alex") != "Welcome to the game, Alex!":
		push_error("[NATIVE SMOKE FAIL] RustSmoke behavior mismatch")
		quit(1)
		return
	print("[NATIVE SMOKE OK]")
	quit(0)

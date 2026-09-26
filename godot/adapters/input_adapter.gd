# Converts action inputs and a single captured screen touch to normalized movement.
class_name InputAdapter
extends RefCounted

const JOYSTICK_RADIUS := 56.0
var touch_index := -1
var touch_origin := Vector2.ZERO
var touch_position := Vector2.ZERO


static func normalized_movement(keyboard: Vector2, touch: Vector2) -> Vector2:
	return (keyboard + touch).limit_length(1.0)


func movement() -> Vector2:
	var keyboard := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	var touch := Vector2.ZERO
	if touch_index >= 0:
		touch = (touch_position - touch_origin) / JOYSTICK_RADIUS
	return normalized_movement(keyboard, touch)


func touch_press(index: int, position: Vector2, joystick_center: Vector2) -> bool:
	if touch_index >= 0 or position.distance_to(joystick_center) > JOYSTICK_RADIUS * 1.5:
		return false
	touch_index = index
	touch_origin = joystick_center
	touch_position = position
	return true


func touch_drag(index: int, position: Vector2) -> void:
	if index == touch_index:
		touch_position = position


func touch_release(index: int) -> void:
	if index == touch_index:
		clear()


func clear() -> void:
	touch_index = -1
	touch_origin = Vector2.ZERO
	touch_position = Vector2.ZERO

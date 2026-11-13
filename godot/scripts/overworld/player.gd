class_name Player
extends Character
## The player. Walk with the arrows, hold B to run, press A to talk or read.

const WALK_TIME := 0.24
const RUN_TIME := 0.13
const TURN_DELAY := 0.09  # a quick tap only turns, like in the DS games

var world  # Overworld
var frozen := false
var _turn_timer := 0.0


func _physics_process(delta: float) -> void:
	if moving or frozen or world == null or world.busy or Engine.get_physics_frames() < world.input_lock_until:
		return
	if Input.is_action_just_pressed("a"):
		world.interact(cell + DIRS[facing])
		return
	if Input.is_action_just_pressed("start"):
		world.open_menu()
		return
	var dir := _held_dir()
	if dir == "":
		_turn_timer = 0.0
		return
	if dir != facing and _turn_timer <= 0.0:
		face(dir)
		_turn_timer = TURN_DELAY
		return
	if _turn_timer > 0.0:
		_turn_timer -= delta
		if _turn_timer > 0.0:
			return
	_try_step(dir)


func _held_dir() -> String:
	# The last pressed direction wins when two are held.
	for d in ["up", "down", "left", "right"]:
		if Input.is_action_just_pressed("move_" + d):
			return d
	if Input.is_action_pressed("move_" + facing):
		return facing
	for d in ["up", "down", "left", "right"]:
		if Input.is_action_pressed("move_" + d):
			return d
	return ""


func _try_step(dir: String) -> void:
	var result: String = world.can_enter(cell, dir)
	if Game.log_text:
		print("[step] ", cell, " ", dir, " -> ", result)
	var t := RUN_TIME if Input.is_action_pressed("b") else WALK_TIME
	match result:
		"ok":
			await walk(dir, t)
			world.on_player_stepped()
		"ledge":
			await walk(dir, WALK_TIME * 1.6, 2, true)
			world.on_player_stepped()
		"exit":
			face(dir)
			world.use_exit_warp(cell)
		_:
			face(dir)

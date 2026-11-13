extends Node
## Global game state: party, bag, story flags and where the player is.

const START_MAP := "test_town"

var party: Array = []  # Array of Mon
var bag: Dictionary = {"pokeball": 5, "potion": 3}
var flags: Dictionary = {}
## Where an "@return" warp (an indoor door mat) leads back to.
var return_point: Dictionary = {}
## Where the player wakes up after losing a battle.
var heal_point: Dictionary = {"map": "test_house", "x": 5, "y": 6, "facing": "down"}

var main: Node  # scripts/main.gd sets this
var log_text := false  # prints every text box to the console (used by the demo run)


func _enter_tree() -> void:
	_setup_input()


func _ready() -> void:
	randomize()
	if party.is_empty():
		var starter := Mon.create("mossfawn", 6)
		party.append(starter)


func lead() -> Mon:
	for m in party:
		if not m.is_fainted():
			return m
	return null


func heal_party() -> void:
	for m in party:
		m.heal_full()


func _setup_input() -> void:
	var keys := {
		"move_up": [KEY_UP, KEY_W],
		"move_down": [KEY_DOWN, KEY_S],
		"move_left": [KEY_LEFT, KEY_A],
		"move_right": [KEY_RIGHT, KEY_D],
		"a": [KEY_Z, KEY_ENTER, KEY_SPACE, KEY_E],
		"b": [KEY_X, KEY_BACKSPACE, KEY_SHIFT, KEY_Q],
		"start": [KEY_ESCAPE, KEY_C],
		"debug_overlay": [KEY_F3],
		"fullscreen": [KEY_F11],
	}
	var pads := {
		"move_up": [JOY_BUTTON_DPAD_UP], "move_down": [JOY_BUTTON_DPAD_DOWN],
		"move_left": [JOY_BUTTON_DPAD_LEFT], "move_right": [JOY_BUTTON_DPAD_RIGHT],
		"a": [JOY_BUTTON_A], "b": [JOY_BUTTON_B], "start": [JOY_BUTTON_START],
	}
	for action in keys:
		if not InputMap.has_action(action):
			InputMap.add_action(action)
		for k in keys[action]:
			var ev := InputEventKey.new()
			ev.physical_keycode = k
			InputMap.action_add_event(action, ev)
		for b in pads.get(action, []):
			var jev := InputEventJoypadButton.new()
			jev.button_index = b
			InputMap.action_add_event(action, jev)


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("fullscreen"):
		var w := get_window()
		w.mode = Window.MODE_WINDOWED if w.mode == Window.MODE_FULLSCREEN else Window.MODE_FULLSCREEN

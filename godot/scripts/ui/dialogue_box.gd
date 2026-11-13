class_name DialogueBox
extends Control
## The text box along the bottom of the screen. `await say(["line", ...])` shows the lines two at a
## time with a typewriter effect; A (or B) moves on.

const CHARS_PER_SEC := 70.0
const BOX := Rect2(4, 132, 312, 44)
const INNER_W := 296

var panel: Panel
var text: Label
var arrow: Label
var _typing := false


func _ready() -> void:
	mouse_filter = MOUSE_FILTER_IGNORE
	set_anchors_preset(PRESET_FULL_RECT)
	panel = Panel.new()
	panel.position = BOX.position
	panel.size = BOX.size
	add_child(panel)
	text = Label.new()
	text.position = Vector2(8, 3)
	text.size = Vector2(INNER_W, 40)
	panel.add_child(text)
	arrow = Label.new()
	arrow.text = "▼"
	arrow.position = Vector2(BOX.size.x - 16, BOX.size.y - 20)
	arrow.add_theme_color_override("font_color", Color("d04040"))
	panel.add_child(arrow)
	hide()


## Splits text into pages of at most two lines that fit the box.
func paginate(lines: Array) -> Array:
	var f: Font = UiTheme.font()
	var pages: Array = []
	for raw in lines:
		var wrapped: Array = []
		var cur := ""
		for word in String(raw).split(" "):
			var trial := word if cur == "" else cur + " " + word
			if f.get_string_size(trial, HORIZONTAL_ALIGNMENT_LEFT, -1, 16).x > INNER_W and cur != "":
				wrapped.append(cur)
				cur = word
			else:
				cur = trial
		wrapped.append(cur)
		for i in range(0, wrapped.size(), 2):
			pages.append("\n".join(wrapped.slice(i, i + 2)))
	return pages


func say(lines: Array, keep_open: bool = false) -> void:
	if Game.log_text:
		print("[text] ", " / ".join(lines))
	show()
	for page in paginate(lines):
		await _type(page)
		arrow.show()
		await _wait_confirm()
		arrow.hide()
	if not keep_open:
		hide()


## Shows text without waiting for a button (used for battle messages that wait on their own).
func show_text(t: String, instant: bool = false) -> void:
	show()
	arrow.hide()
	if instant:
		text.text = t
		text.visible_characters = -1
	else:
		await _type(t)


func _type(page: String) -> void:
	arrow.hide()
	text.text = page
	text.visible_characters = 0
	_typing = true
	var shown := 0.0
	var total := page.length()
	while shown < total:
		await get_tree().process_frame
		if Input.is_action_just_pressed("a") or Input.is_action_just_pressed("b"):
			break
		shown += CHARS_PER_SEC * get_process_delta_time()
		text.visible_characters = int(shown)
	text.visible_characters = -1
	_typing = false
	await get_tree().process_frame


func _wait_confirm() -> void:
	var t := 0.0
	while true:
		await get_tree().process_frame
		t += get_process_delta_time()
		arrow.visible = fmod(t, 0.8) < 0.5
		if Input.is_action_just_pressed("a") or Input.is_action_just_pressed("b"):
			return

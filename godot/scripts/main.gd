extends Node
## Root of the game. Owns the overworld, the text box, the battle screen and the screen fades.

var overworld: Overworld
var ui: CanvasLayer
var dialogue: DialogueBox
var battle_layer: CanvasLayer
var battle: BattleScene
var fader: ColorRect
var location: Panel
var location_label: Label


func _ready() -> void:
	Game.main = self
	var theme := UiTheme.make()
	overworld = Overworld.new()
	add_child(overworld)

	battle_layer = CanvasLayer.new()
	battle_layer.layer = 5
	add_child(battle_layer)
	battle = BattleScene.new()
	battle.theme = theme
	battle_layer.add_child(battle)

	ui = CanvasLayer.new()
	ui.layer = 10
	add_child(ui)
	var root := Control.new()
	root.theme = theme
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	ui.add_child(root)
	dialogue = DialogueBox.new()
	root.add_child(dialogue)
	location = Panel.new()
	location.position = Vector2(4, -30)
	location.size = Vector2(140, 22)
	root.add_child(location)
	location_label = Label.new()
	location_label.position = Vector2(8, 0)
	location.add_child(location_label)

	var fade_layer := CanvasLayer.new()
	fade_layer.layer = 50
	add_child(fade_layer)
	fader = ColorRect.new()
	fader.color = Color(0, 0, 0, 0)
	fader.set_anchors_preset(Control.PRESET_FULL_RECT)
	fader.mouse_filter = Control.MOUSE_FILTER_IGNORE
	fade_layer.add_child(fader)

	var start: Dictionary = MapData.load_map(Game.START_MAP).meta.get("player_start", {"x": 5, "y": 5, "facing": "down"})
	overworld.enter_map(Game.START_MAP, Vector2i(int(start["x"]), int(start["y"])), start.get("facing", "down"))
	show_location(overworld.map.meta.get("name", Game.START_MAP))

	if OS.get_cmdline_user_args().has("--demo"):
		var demo = load("res://scripts/tools/demo.gd").new()
		add_child(demo)


func say(lines: Array) -> void:
	await dialogue.say(lines)


func fade_out(t: float = 0.25, color: Color = Color.BLACK) -> void:
	fader.color = Color(color, fader.color.a)
	var tw := create_tween()
	tw.tween_property(fader, "color:a", 1.0, t)
	await tw.finished


func fade_in(t: float = 0.25) -> void:
	var tw := create_tween()
	tw.tween_property(fader, "color:a", 0.0, t)
	await tw.finished


func show_location(text: String) -> void:
	location_label.text = text
	location.size.x = UiTheme.font().get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, 16).x + 18
	var tw := create_tween()
	tw.tween_property(location, "position:y", 4.0, 0.25)
	tw.tween_interval(1.8)
	tw.tween_property(location, "position:y", -30.0, 0.25)


## Wild battle with the classic flash and fade in. Returns "won", "ran", "caught" or "lost".
func run_battle(wild: Mon) -> String:
	for i in 2:
		await fade_out(0.08, Color.WHITE)
		await fade_in(0.08)
	await fade_out(0.35)
	overworld.visible = false
	battle.show()
	fade_in(0.3)  # runs while the battle's intro starts
	var result: String = await battle.run(wild)
	overworld.visible = true
	await fade_in(0.3)
	return result

extends Node
## Scripted play-through that takes screenshots. Run with:
##   godot --path godot -- --demo --shots=/some/folder
## Used to check the game without a person at the keyboard.

var out_dir := "user://shots"
var n := 0


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--shots="):
			out_dir = a.substr(8)
	DirAccess.make_dir_recursive_absolute(out_dir)
	seed(7)
	Game.log_text = true
	_run()


func wait(sec: float) -> void:
	await get_tree().create_timer(sec).timeout


func hold(action: String, down: bool) -> void:
	# Sent as input events so the game sees them exactly like real key presses.
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = down
	Input.parse_input_event(ev)


func press(action: String, time: float = 0.1) -> void:
	hold(action, true)
	await wait(time)
	hold(action, false)
	await wait(0.05)


func shot(name: String) -> void:
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.resize(img.get_width() * 4, img.get_height() * 4, Image.INTERPOLATE_NEAREST)
	n += 1
	img.save_png("%s/%02d_%s.png" % [out_dir, n, name])
	print("shot ", name)


func _run() -> void:
	var main = Game.main
	var ow: Overworld = main.overworld
	await wait(0.8)
	await shot("town_start")
	# Walk a few steps along the path.
	await press("move_right", 0.9)
	await wait(0.3)
	await shot("town_walk")
	# Talk to the old man.
	ow.player.place(Vector2i(22, 11), "right")
	await wait(0.2)
	await press("a")
	await wait(1.0)
	await shot("dialogue")
	for i in 2:
		await press("a")
		await wait(0.6)
	# Enter the house.
	ow.player.place(Vector2i(8, 13), "up")
	await wait(0.2)
	await press("move_up", 0.3)
	await wait(1.0)
	await shot("house")
	await press("move_down", 0.15)
	await wait(1.0)
	await shot("back_outside")
	# Walk north out of town into the route without a loading screen.
	ow.player.place(Vector2i(20, 4), "up")
	await wait(0.2)
	hold("move_up", true)
	await wait(1.1)
	await shot("town_to_route")
	await wait(0.9)
	hold("move_up", false)
	await wait(0.3)
	await shot("route")
	# Tall grass on the route, with the debug grid.
	ow.player.place(Vector2i(28, 18), "left")
	ow.debug_layer.visible = true
	await wait(0.3)
	await shot("debug_overlay")
	ow.debug_layer.visible = false
	await wait(0.2)
	await shot("in_grass")
	# A wild battle.
	ow.busy = true
	var wild := Mon.create("pixling", 4)
	var done := [false]
	var go := func():
		var r: String = await main.run_battle(wild)
		print("battle result: ", r)
		done[0] = true
	go.call()
	await wait(2.2)
	await shot("battle_intro")
	await press("a")
	await wait(1.0)
	await press("a")
	await wait(0.6)
	await shot("battle_menu")
	await press("a")  # FIGHT
	await wait(0.3)
	await shot("battle_moves")
	await press("a")  # first move
	await wait(1.6)
	await shot("battle_attack")
	var guard := 0
	while not done[0] and guard < 80:
		guard += 1
		if main.battle.menu_layer.get_child_count() > 0:
			await press("a")  # FIGHT, then the first move again
			await wait(0.2)
			await press("a")
		else:
			await press("a")
		await wait(0.5)
		if guard == 6:
			await shot("battle_mid")
	await wait(1.0)
	await shot("after_battle")
	get_tree().quit()

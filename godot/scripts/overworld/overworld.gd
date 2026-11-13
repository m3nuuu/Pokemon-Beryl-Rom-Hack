class_name Overworld
extends Node2D
## Shows the current painted map and its connected neighbours, moves the player, and runs warps,
## signs, NPC talk and wild encounters.
##
## Layers, back to front: ground pictures, characters (sorted by their feet), overlay pictures
## (roofs, tree tops, the top of tall grass), debug grid (F3).

const CELL := 16
const ENCOUNTER_RATE := 0.1  # per step in tall grass

var map: MapData
var neighbours: Dictionary = {}  # direction -> {"map": MapData, "origin": Vector2i (cells)}
var busy := false  # true while a dialogue, warp or battle runs

var ground_layer: Node2D
var entities: Node2D
var overlay_layer: Node2D
var debug_layer: Node2D
var camera: Camera2D
var player: Player
var npcs: Array = []
var _map_cache: Dictionary = {}
var _steps_since_battle := 0
## Input is ignored for a couple of frames after a dialogue closes, so the same A press does not
## start it again.
var input_lock_until := 0


func _release() -> void:
	busy = false
	input_lock_until = Engine.get_physics_frames() + 3


func _ready() -> void:
	ground_layer = Node2D.new()
	ground_layer.z_index = -10
	add_child(ground_layer)
	entities = Node2D.new()
	entities.y_sort_enabled = true
	add_child(entities)
	overlay_layer = Node2D.new()
	overlay_layer.z_index = 10
	add_child(overlay_layer)
	debug_layer = preload("res://scripts/overworld/debug_overlay.gd").new()
	debug_layer.z_index = 20
	debug_layer.world = self
	debug_layer.visible = false
	add_child(debug_layer)
	camera = Camera2D.new()
	add_child(camera)
	camera.make_current()
	player = Player.new()
	player.world = self
	player.setup(load("res://assets/characters/player.png"))
	entities.add_child(player)


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("debug_overlay"):
		debug_layer.visible = not debug_layer.visible
		debug_layer.queue_redraw()


func _process(_delta: float) -> void:
	_update_camera()


func get_map(map_id: String) -> MapData:
	if not _map_cache.has(map_id):
		_map_cache[map_id] = MapData.load_map(map_id)
	return _map_cache[map_id]


## Loads a map and puts the player on `cell`.
func enter_map(map_id: String, cell: Vector2i, facing: String) -> void:
	_build(map_id)
	player.place(cell, facing)
	_update_camera()
	camera.reset_smoothing()


func _build(map_id: String) -> void:
	map = get_map(map_id)
	for n in ground_layer.get_children():
		n.queue_free()
	for n in overlay_layer.get_children():
		n.queue_free()
	for n in npcs:
		n.queue_free()
	npcs.clear()
	neighbours.clear()
	_add_picture(map, Vector2i.ZERO)
	for dir in map.connections():
		var c: Dictionary = map.connections()[dir]
		var nb := get_map(c["map"])
		if nb == null:
			continue
		var off := int(c.get("offset", 0))
		var origin := Vector2i.ZERO
		match dir:
			"north": origin = Vector2i(off, -nb.height)
			"south": origin = Vector2i(off, map.height)
			"west": origin = Vector2i(-nb.width, off)
			"east": origin = Vector2i(map.width, off)
		neighbours[dir] = {"map": nb, "origin": origin}
		_add_picture(nb, origin)
	for data in map.meta.get("npcs", []):
		var npc := Npc.new()
		entities.add_child(npc)
		npc.setup_npc(data, self)
		npcs.append(npc)
	debug_layer.queue_redraw()


func _add_picture(m: MapData, origin: Vector2i) -> void:
	var g := Sprite2D.new()
	g.texture = m.ground
	g.centered = false
	g.position = Vector2(origin * CELL)
	ground_layer.add_child(g)
	if m.overlay:
		var o := Sprite2D.new()
		o.texture = m.overlay
		o.centered = false
		o.position = Vector2(origin * CELL)
		overlay_layer.add_child(o)


func _update_camera() -> void:
	if map == null:
		return
	var view := get_viewport_rect().size
	var target := player.position + Vector2(0, -8)
	# Limits: the map's own edges, pushed outwards on sides that connect to another map.
	var lo := Vector2.ZERO
	var hi := map.size_px()
	for dir in neighbours:
		var nb: MapData = neighbours[dir]["map"]
		match dir:
			"north": lo.y -= nb.size_px().y
			"south": hi.y += nb.size_px().y
			"west": lo.x -= nb.size_px().x
			"east": hi.x += nb.size_px().x
	var pos := target
	for axis in 2:
		if hi[axis] - lo[axis] <= view[axis]:
			pos[axis] = (lo[axis] + hi[axis]) / 2.0  # small rooms sit in the middle of the screen
		else:
			pos[axis] = clamp(target[axis], lo[axis] + view[axis] / 2.0, hi[axis] - view[axis] / 2.0)
	camera.position = pos.round()


# ------------------------------------------------------------------ grid queries

## What kind of ground a cell is, looking into connected maps when the cell is off this map.
func kind_at(cell: Vector2i) -> String:
	if map.in_bounds(cell):
		return map.kind_at(cell)
	for dir in neighbours:
		var nb: MapData = neighbours[dir]["map"]
		var local: Vector2i = cell - neighbours[dir]["origin"]
		if nb.in_bounds(local):
			return nb.kind_at(local)
	return "block"


func npc_at(cell: Vector2i) -> Npc:
	for n in npcs:
		if n.cell == cell:
			return n
	return null


## "ok", "ledge" (jump down two cells), "exit" (step off a door mat) or "blocked".
func can_enter(from: Vector2i, dir: String, mover: Node = null) -> String:
	var to: Vector2i = from + Character.DIRS[dir]
	if mover == null:
		var here = map.warp_at(from)
		if here != null and here.get("exit", "") == dir:
			return "exit"
	if npc_at(to) != null:
		return "blocked"
	if mover != null and (to == player.cell or map.warp_at(to) != null or not map.in_bounds(to)):
		return "blocked"
	var k := kind_at(to)
	match k:
		"walk", "grass":
			return "ok"
		"ledge":
			if dir == "down" and kind_at(to + Vector2i(0, 1)) != "block" and npc_at(to + Vector2i(0, 1)) == null:
				return "ledge"
	return "blocked"


# ------------------------------------------------------------------ events

func on_player_stepped() -> void:
	# Crossed into a connected map: rebuild around it. Everything stays where it was on screen.
	if not map.in_bounds(player.cell):
		for dir in neighbours:
			var nb: MapData = neighbours[dir]["map"]
			var origin: Vector2i = neighbours[dir]["origin"]
			var local: Vector2i = player.cell - origin
			if nb.in_bounds(local):
				var shift := Vector2(origin * CELL)
				_build(nb.id)
				player.place(local)
				camera.position -= shift
				camera.reset_smoothing()
				_show_map_name()
				break
		return
	var warp = map.warp_at(player.cell)
	if warp != null and not warp.has("exit"):
		await _do_warp(warp)
		return
	if map.kind_at(player.cell) == "grass":
		_steps_since_battle += 1
		if _steps_since_battle > 2 and randf() < ENCOUNTER_RATE:
			_start_wild_battle()


func use_exit_warp(cell: Vector2i) -> void:
	var warp = map.warp_at(cell)
	if warp != null:
		await _do_warp(warp)


func _do_warp(warp: Dictionary) -> void:
	busy = true
	var target_map: String = warp["to"]
	var target_cell := Vector2i(int(warp.get("to_x", 0)), int(warp.get("to_y", 0)))
	var target_facing: String = warp.get("facing", "down")
	if target_map == "@return":
		var r := Game.return_point
		target_map = r.get("map", Game.START_MAP)
		target_cell = Vector2i(int(r.get("x", 0)), int(r.get("y", 0)))
		target_facing = r.get("facing", "down")
	else:
		# Remember the door so the mat inside leads back out under it.
		Game.return_point = {"map": map.id, "x": player.cell.x, "y": player.cell.y + 1, "facing": "down"}
	await Game.main.fade_out()
	enter_map(target_map, target_cell, target_facing)
	await Game.main.fade_in()
	_release()


func interact(cell: Vector2i) -> void:
	var npc := npc_at(cell)
	if npc != null:
		busy = true
		npc.talking = true
		npc.face(Character.dir_name(player.cell - npc.cell))
		await Game.main.say(npc.info.get("dialogue", ["..."]))
		if npc.info.get("action", "") == "heal":
			Game.heal_party()
		npc.talking = false
		_release()
		return
	var s = map.sign_at(cell)
	if s != null:
		busy = true
		await Game.main.say(s.get("text", []))
		_release()


func open_menu() -> void:
	busy = true
	var lines: Array = ["Party:"]
	for m in Game.party:
		lines.append("%s  Lv.%d  HP %d/%d" % [m.display_name(), m.level, m.hp, m.max_hp()])
	lines.append("(The full menu comes in a later version.)")
	await Game.main.say(lines)
	_release()


func _show_map_name() -> void:
	Game.main.show_location(map.meta.get("name", map.id))


func _start_wild_battle() -> void:
	var table: Array = map.meta.get("encounters", {}).get("grass", [])
	if table.is_empty() or Game.lead() == null:
		return
	var total := 0
	for e in table:
		total += int(e.get("weight", 1))
	var roll: int = randi() % maxi(total, 1)
	var pick: Dictionary = table[0]
	for e in table:
		roll -= int(e.get("weight", 1))
		if roll < 0:
			pick = e
			break
	if not Data.species.has(pick["species"]):
		push_warning("Unknown species in encounter table: " + str(pick["species"]))
		return
	_steps_since_battle = 0
	busy = true
	var wild := Mon.create(pick["species"], randi_range(int(pick["min"]), int(pick["max"])))
	var result: String = await Game.main.run_battle(wild)
	if result == "lost":
		var h := Game.heal_point
		await Game.main.fade_out()
		Game.heal_party()
		enter_map(h["map"], Vector2i(int(h["x"]), int(h["y"])), h["facing"])
		await Game.main.fade_in()
		await Game.main.say(["You hurried home to rest...", "Your POKéMON are healed."])
	_release()

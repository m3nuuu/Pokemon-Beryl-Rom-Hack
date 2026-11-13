class_name Npc
extends Character
## A person on the map. Data comes from the "npcs" list in map.json:
##   {"id", "x", "y", "sprite", "facing", "wander", "dialogue": [...], "action": "heal"}

var info: Dictionary = {}
var home := Vector2i.ZERO
var world  # Overworld
var talking := false
var _wait := 0.0


func setup_npc(data: Dictionary, w) -> void:
	info = data
	world = w
	var sheet_path := "res://assets/characters/%s.png" % data.get("sprite", "npc_girl")
	if not ResourceLoader.exists(sheet_path):
		sheet_path = "res://assets/characters/npc_girl.png"
	setup(load(sheet_path))
	home = Vector2i(int(data["x"]), int(data["y"]))
	place(home, data.get("facing", "down"))
	_wait = randf_range(1.0, 3.0)


func _process(delta: float) -> void:
	if not info.get("wander", false) or moving or talking or world == null or world.busy:
		return
	_wait -= delta
	if _wait > 0.0:
		return
	_wait = randf_range(1.5, 4.0)
	var dir: String = DIRS.keys()[randi() % 4]
	var target: Vector2i = cell + DIRS[dir]
	if (target - home).length() > 2.0 or world.can_enter(cell, dir, self) != "ok":
		face(dir)
		return
	walk(dir, 0.3)

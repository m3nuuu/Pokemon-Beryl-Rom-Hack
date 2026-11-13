extends Node2D
## F3 in game: shows the 16px grid and what each cell does, on top of the painted map.
## The same colours as gameplay.png: black blocked, green tall grass, blue water, orange ledge.
## Warps are magenta, signs yellow, NPCs cyan.

var world  # Overworld

const FILL := {
	"block": Color(0, 0, 0, 0.45),
	"grass": Color(0, 0.8, 0, 0.35),
	"water": Color(0, 0.3, 1, 0.4),
	"ledge": Color(1, 0.63, 0, 0.5),
}


func _draw() -> void:
	if world == null or world.map == null:
		return
	var m: MapData = world.map
	var c := MapData.CELL
	for y in m.height:
		for x in m.width:
			var k := m.kind_at(Vector2i(x, y))
			if FILL.has(k):
				draw_rect(Rect2(x * c, y * c, c, c), FILL[k])
	var line := Color(1, 1, 1, 0.18)
	for x in m.width + 1:
		draw_line(Vector2(x * c, 0), Vector2(x * c, m.height * c), line)
	for y in m.height + 1:
		draw_line(Vector2(0, y * c), Vector2(m.width * c, y * c), line)
	for w in m.meta.get("warps", []):
		draw_rect(Rect2(int(w["x"]) * c + 1, int(w["y"]) * c + 1, c - 2, c - 2), Color(1, 0, 1, 0.9), false, 2.0)
	for s in m.meta.get("signs", []):
		draw_rect(Rect2(int(s["x"]) * c + 1, int(s["y"]) * c + 1, c - 2, c - 2), Color(1, 1, 0, 0.9), false, 2.0)
	for n in m.meta.get("npcs", []):
		draw_rect(Rect2(int(n["x"]) * c + 1, int(n["y"]) * c + 1, c - 2, c - 2), Color(0, 1, 1, 0.9), false, 2.0)


func _process(_delta: float) -> void:
	if visible:
		queue_redraw()

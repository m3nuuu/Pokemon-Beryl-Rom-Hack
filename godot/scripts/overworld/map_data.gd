class_name MapData
extends RefCounted
## One painted map: maps/<id>/ground.png, overlay.png, gameplay.png and map.json.
##
## gameplay.png is the colour key. It can be one pixel per 16x16 grid cell (small and quick to
## edit), or the same size as ground.png (paint it as a layer over the picture). For a full-size
## key the colour in the middle of each cell counts. See docs/DRAWING_GUIDE.md.

const CELL := 16

## Key colours. The nearest one wins, so slightly off colours from a soft brush still work.
const KEY_COLORS := {
	"walk": Color8(255, 255, 255),
	"block": Color8(0, 0, 0),
	"grass": Color8(0, 200, 0),
	"water": Color8(0, 80, 255),
	"ledge": Color8(255, 160, 0),
}

var id: String
var meta: Dictionary = {}
var ground: Texture2D
var overlay: Texture2D
var width: int  # in cells
var height: int
var kinds: PackedStringArray = []


static func load_map(map_id: String) -> MapData:
	var m := MapData.new()
	m.id = map_id
	var dir := "res://maps/%s/" % map_id
	var f := FileAccess.open(dir + "map.json", FileAccess.READ)
	if f == null:
		push_error("Map %s has no map.json" % map_id)
		return null
	var parsed = JSON.parse_string(f.get_as_text())
	m.meta = parsed if parsed is Dictionary else {}
	m.ground = load(dir + "ground.png")
	if ResourceLoader.exists(dir + "overlay.png"):
		m.overlay = load(dir + "overlay.png")
	m.width = int(ceil(m.ground.get_width() / float(CELL)))
	m.height = int(ceil(m.ground.get_height() / float(CELL)))
	m._read_key(dir + "gameplay.png")
	return m


func _read_key(path: String) -> void:
	kinds.resize(width * height)
	kinds.fill("walk")
	if not ResourceLoader.exists(path):
		push_warning("Map %s has no gameplay.png, everything is walkable" % id)
		return
	var img: Image = (load(path) as Texture2D).get_image()
	if img.is_compressed():
		img.decompress()
	var per_cell := img.get_width() == width and img.get_height() == height
	for y in height:
		for x in width:
			var px := Vector2i(x, y) if per_cell else Vector2i(x * CELL + CELL / 2, y * CELL + CELL / 2)
			if px.x >= img.get_width() or px.y >= img.get_height():
				continue
			kinds[y * width + x] = _nearest_kind(img.get_pixelv(px))


static func _nearest_kind(c: Color) -> String:
	if c.a < 0.5:
		return "walk"
	var best := "walk"
	var best_d := INF
	for k in KEY_COLORS:
		var kc: Color = KEY_COLORS[k]
		var d := Vector3(c.r - kc.r, c.g - kc.g, c.b - kc.b).length_squared()
		if d < best_d:
			best_d = d
			best = k
	return best


func size_px() -> Vector2:
	return Vector2(ground.get_width(), ground.get_height())


func in_bounds(cell: Vector2i) -> bool:
	return cell.x >= 0 and cell.y >= 0 and cell.x < width and cell.y < height


func kind_at(cell: Vector2i) -> String:
	if not in_bounds(cell):
		return "block"
	return kinds[cell.y * width + cell.x]


func connections() -> Dictionary:
	return meta.get("connections", {})


func warp_at(cell: Vector2i):
	for w in meta.get("warps", []):
		if int(w["x"]) == cell.x and int(w["y"]) == cell.y:
			return w
	return null


func sign_at(cell: Vector2i):
	for s in meta.get("signs", []):
		if int(s["x"]) == cell.x and int(s["y"]) == cell.y:
			return s
	return null

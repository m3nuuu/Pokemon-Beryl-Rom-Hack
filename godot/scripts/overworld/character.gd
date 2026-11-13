class_name Character
extends Node2D
## A walking character on the 16px grid. Sprite sheets have 32x32 frames: three columns (stand,
## step A, step B) and four rows (down, up, left, right).

signal step_finished

const CELL := 16
const DIRS := {
	"down": Vector2i(0, 1), "up": Vector2i(0, -1), "left": Vector2i(-1, 0), "right": Vector2i(1, 0),
}
const ROWS := {"down": 0, "up": 1, "left": 2, "right": 3}

var cell := Vector2i.ZERO
var facing := "down"
var moving := false
var sprite: Sprite2D
var _step_parity := false
var _anim_t := 0.0
var _anim_len := 0.0


func setup(sheet: Texture2D) -> void:
	sprite = Sprite2D.new()
	sprite.texture = sheet
	sprite.hframes = 3
	sprite.vframes = 4
	sprite.centered = false
	sprite.offset = Vector2(-16, -32)
	add_child(sprite)
	_update_frame(0)


## Pixel position of a cell: the feet stand on the bottom middle of the cell.
static func cell_to_pos(c: Vector2i) -> Vector2:
	return Vector2(c.x * CELL + CELL / 2, c.y * CELL + CELL)


func place(c: Vector2i, face: String = "") -> void:
	cell = c
	position = cell_to_pos(c)
	if face != "":
		facing = face
	_update_frame(0)


func face(dir: String) -> void:
	facing = dir
	_update_frame(0)


static func dir_name(v: Vector2i) -> String:
	for k in DIRS:
		if DIRS[k] == v:
			return k
	return "down"


## Moves one cell (or `cells` cells, for ledge jumps) over `duration` seconds.
func walk(dir: String, duration: float, cells: int = 1, hop: bool = false) -> void:
	facing = dir
	moving = true
	_step_parity = not _step_parity
	var target: Vector2i = cell + DIRS[dir] * cells
	var from := position
	var to := cell_to_pos(target)
	cell = target
	_anim_t = 0.0
	_anim_len = duration
	var tw := create_tween()
	tw.tween_method(func(t: float):
		position = from.lerp(to, t).round()
		if hop:
			sprite.position.y = -round(sin(t * PI) * 10.0)
		_anim_t = t
		_update_frame(1 if t < 0.5 else 0)
	, 0.0, 1.0, duration)
	await tw.finished
	sprite.position.y = 0
	moving = false
	_update_frame(0)
	step_finished.emit()


func _update_frame(phase: int) -> void:
	if sprite == null:
		return
	var col := 0
	if phase == 1:
		col = 1 if _step_parity else 2
	sprite.frame = ROWS[facing] * 3 + col

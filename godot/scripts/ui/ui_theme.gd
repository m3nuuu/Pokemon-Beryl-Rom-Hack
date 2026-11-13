class_name UiTheme
extends RefCounted
## Fonts and box styles shared by every screen. Pixel fonts are set to render without smoothing.

const TEXT := Color("2a2a32")
const TEXT_SHADOW := Color("c8c8d0")

static var _font: FontFile
static var _small: FontFile


static func font() -> FontFile:
	if _font == null:
		_font = _pixel(load("res://assets/fonts/PixelifySans.ttf"))
	return _font


## Small font for HP numbers and levels.
static func small_font() -> FontFile:
	if _small == null:
		_small = _pixel(load("res://assets/fonts/Jersey10.ttf"))
	return _small


static func _pixel(f: FontFile) -> FontFile:
	f.antialiasing = TextServer.FONT_ANTIALIASING_NONE
	f.hinting = TextServer.HINTING_NONE
	f.subpixel_positioning = TextServer.SUBPIXEL_POSITIONING_DISABLED
	f.generate_mipmaps = false
	return f


static func box(fill: Color = Color("f8f8f8"), border: Color = Color("3a4a5a"), radius: int = 4, border_w: int = 2) -> StyleBoxFlat:
	var s := StyleBoxFlat.new()
	s.bg_color = fill
	s.border_color = border
	s.set_border_width_all(border_w)
	s.set_corner_radius_all(radius)
	s.anti_aliasing = false
	s.set_content_margin_all(4)
	return s


static func make() -> Theme:
	var t := Theme.new()
	t.default_font = font()
	t.default_font_size = 16
	t.set_color("font_color", "Label", TEXT)
	t.set_color("font_shadow_color", "Label", TEXT_SHADOW)
	t.set_constant("shadow_offset_x", "Label", 1)
	t.set_constant("shadow_offset_y", "Label", 1)
	t.set_constant("line_spacing", "Label", -3)
	t.set_stylebox("panel", "Panel", box())
	return t


static func label(text: String, pos: Vector2, size: int = 16, color: Color = TEXT, shadow: bool = true) -> Label:
	var l := Label.new()
	l.text = text
	l.position = pos
	if size != 16:
		l.add_theme_font_override("font", small_font() if size <= 10 else font())
		l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", color)
	if not shadow:
		l.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0))
	return l

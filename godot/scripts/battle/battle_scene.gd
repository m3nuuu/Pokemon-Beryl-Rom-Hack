class_name BattleScene
extends Control
## Classic turn-based battle on one 320x180 screen: the two Pokémon and their HP boxes on top, the
## message box and the menus along the bottom.
##
##   var result: String = await battle.run(wild_mon)   # "won", "ran", "caught" or "lost"

const ENEMY_BASE := Vector2(236, 86)   # middle bottom of the far platform
const PLAYER_BASE := Vector2(82, 158)   # middle bottom of the near platform
const STAGE_NAMES := {"atk": "ATTACK", "def": "DEFENSE", "spa": "SP. ATK", "spd": "SP. DEF", "spe": "SPEED", "acc": "accuracy", "eva": "evasiveness"}

var enemy: Mon
var player: Mon
var stages := {"player": {}, "enemy": {}}
var msg: DialogueBox

var bg: TextureRect
var enemy_sprite: TextureRect
var player_sprite: TextureRect
var enemy_box: Panel
var player_box: Panel
var enemy_hp_bar: ColorRect
var player_hp_bar: ColorRect
var player_exp_bar: ColorRect
var enemy_name: Label
var enemy_lv: Label
var player_name: Label
var player_lv: Label
var player_hp_text: Label
var menu_layer: Control


func _ready() -> void:
	set_anchors_preset(PRESET_FULL_RECT)
	mouse_filter = MOUSE_FILTER_IGNORE
	bg = TextureRect.new()
	bg.texture = load("res://assets/battle/bg_grass.png")
	add_child(bg)
	enemy_sprite = _sprite_rect()
	player_sprite = _sprite_rect()
	player_sprite.flip_h = true
	_build_enemy_box()
	_build_player_box()
	msg = DialogueBox.new()
	add_child(msg)
	menu_layer = Control.new()
	menu_layer.mouse_filter = MOUSE_FILTER_IGNORE
	add_child(menu_layer)
	hide()


func _sprite_rect() -> TextureRect:
	var r := TextureRect.new()
	r.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	r.stretch_mode = TextureRect.STRETCH_SCALE
	add_child(r)
	return r


func _build_enemy_box() -> void:
	enemy_box = Panel.new()
	enemy_box.position = Vector2(6, 8)
	enemy_box.size = Vector2(134, 32)
	enemy_box.add_theme_stylebox_override("panel", UiTheme.box(Color("f4f4ec"), Color("3a4a5a"), 3))
	add_child(enemy_box)
	enemy_name = UiTheme.label("", Vector2(6, -1))
	enemy_box.add_child(enemy_name)
	enemy_lv = _right_label(Vector2(84, -1), 44)
	enemy_box.add_child(enemy_lv)
	enemy_hp_bar = _hp_bar(enemy_box, Vector2(34, 21), 92)


func _build_player_box() -> void:
	player_box = Panel.new()
	player_box.position = Vector2(182, 84)
	player_box.size = Vector2(134, 46)
	player_box.add_theme_stylebox_override("panel", UiTheme.box(Color("f4f4ec"), Color("3a4a5a"), 3))
	add_child(player_box)
	player_name = UiTheme.label("", Vector2(6, -1))
	player_box.add_child(player_name)
	player_lv = _right_label(Vector2(84, -1), 44)
	player_box.add_child(player_lv)
	player_hp_bar = _hp_bar(player_box, Vector2(34, 19), 92)
	player_hp_text = _right_label(Vector2(58, 21), 70)
	player_box.add_child(player_hp_text)
	var exp_bg := ColorRect.new()
	exp_bg.color = Color("404858")
	exp_bg.position = Vector2(6, 40)
	exp_bg.size = Vector2(122, 2)
	player_box.add_child(exp_bg)
	player_exp_bar = ColorRect.new()
	player_exp_bar.color = Color("48a8f0")
	player_exp_bar.position = exp_bg.position
	player_exp_bar.size = Vector2(0, 2)
	player_box.add_child(player_exp_bar)


func _right_label(pos: Vector2, width: int) -> Label:
	var l := UiTheme.label("", pos)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	l.size = Vector2(width, 18)
	return l


func _hp_bar(parent: Control, pos: Vector2, width: int) -> ColorRect:
	var label := UiTheme.label("HP", pos + Vector2(-20, -6), 16, Color("e8a020"))
	parent.add_child(label)
	var back := ColorRect.new()
	back.color = Color("404858")
	back.position = pos
	back.size = Vector2(width, 5)
	parent.add_child(back)
	var bar := ColorRect.new()
	bar.position = pos + Vector2(1, 1)
	bar.size = Vector2(width - 2, 3)
	bar.color = Color("58d080")
	parent.add_child(bar)
	bar.set_meta("full", width - 2)
	return bar


# ------------------------------------------------------------------ main loop

func run(wild: Mon) -> String:
	enemy = wild
	player = Game.lead()
	stages = {"player": _fresh_stages(), "enemy": _fresh_stages()}
	_show_mon("enemy")
	_show_mon("player")
	menu_layer.get_children().map(func(n): n.queue_free())
	show()
	await _intro()
	while true:
		var action: Dictionary = await _choose_action()
		var result := await _play_turn(action)
		if result != "":
			await _outro()
			return result
	return "ran"


func _fresh_stages() -> Dictionary:
	return {"atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0, "acc": 0, "eva": 0}


func _show_mon(side: String) -> void:
	var m: Mon = enemy if side == "enemy" else player
	var tex := Data.front_sprite(m.species_id)
	var rect: TextureRect = enemy_sprite if side == "enemy" else player_sprite
	if side == "player":
		var back := Data.back_sprite(m.species_id)
		rect.flip_h = back == null  # no back sprite yet: show the front one, mirrored
		if back != null:
			tex = back
	rect.texture = tex
	var size := Vector2(64, 64) if tex == null else tex.get_size()
	var scale := 1.0
	if side == "player" and size.y <= 64:
		scale = 2.0  # the near Pokémon is drawn bigger, like the camera is behind it
	rect.size = size * scale
	var base := ENEMY_BASE if side == "enemy" else PLAYER_BASE
	rect.position = (base - Vector2(rect.size.x / 2.0, rect.size.y)).round()
	rect.modulate = Color.WHITE
	rect.show()
	_refresh_box(side, true)


func _refresh_box(side: String, instant: bool = false) -> void:
	var m: Mon = enemy if side == "enemy" else player
	var name_l: Label = enemy_name if side == "enemy" else player_name
	var lv_l: Label = enemy_lv if side == "enemy" else player_lv
	name_l.text = m.display_name()
	lv_l.text = _status_tag(m) + "Lv%d" % m.level
	if side == "player":
		player_hp_text.text = "%d/%d" % [max(m.hp, 0), m.max_hp()]
		var lo := Mon.exp_for_level(m.level)
		var hi := Mon.exp_for_level(m.level + 1)
		player_exp_bar.size.x = 122.0 * clamp(float(m.exp - lo) / max(hi - lo, 1), 0.0, 1.0)
	if instant:
		_set_bar(enemy_hp_bar if side == "enemy" else player_hp_bar, float(max(m.hp, 0)) / m.max_hp())


func _status_tag(m: Mon) -> String:
	return "" if m.status == "" else m.status.to_upper() + " "


func _set_bar(bar: ColorRect, frac: float) -> void:
	bar.size.x = round(float(bar.get_meta("full")) * frac)
	bar.color = Color("58d080") if frac > 0.5 else (Color("f0c040") if frac > 0.2 else Color("e85040"))


func _animate_hp(side: String, from_hp: int, to_hp: int) -> void:
	var m: Mon = enemy if side == "enemy" else player
	var bar: ColorRect = enemy_hp_bar if side == "enemy" else player_hp_bar
	var steps: int = max(1, abs(from_hp - to_hp))
	var dur: float = clamp(steps * 0.03, 0.25, 0.9)
	var t := 0.0
	while t < dur:
		await get_tree().process_frame
		t += get_process_delta_time()
		var hp_now := lerpf(from_hp, to_hp, min(t / dur, 1.0))
		_set_bar(bar, max(hp_now, 0.0) / m.max_hp())
		if side == "player":
			player_hp_text.text = "%d/%d" % [int(round(max(hp_now, 0.0))), m.max_hp()]
	_refresh_box(side, true)


func _say(lines: Array) -> void:
	await msg.say(lines, true)


# ------------------------------------------------------------------ intro and outro

func _intro() -> void:
	var e_target := enemy_sprite.position
	var p_target := player_sprite.position
	enemy_sprite.position.x = -enemy_sprite.size.x
	player_sprite.position.x = 320
	enemy_box.position.x = -140
	player_box.position.x = 330
	msg.show_text("", true)
	var tw := create_tween().set_parallel()
	tw.tween_property(enemy_sprite, "position:x", e_target.x, 0.7).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	tw.tween_property(player_sprite, "position:x", p_target.x, 0.7).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	await tw.finished
	var tb := create_tween()
	tb.tween_property(enemy_box, "position:x", 6.0, 0.25)
	await _say(["A wild %s appeared!" % enemy.display_name()])
	var tp := create_tween()
	tp.tween_property(player_box, "position:x", 186.0, 0.25)
	await _say(["Go! %s!" % player.display_name()])


func _outro() -> void:
	await Game.main.fade_out()
	msg.hide()
	hide()


# ------------------------------------------------------------------ menus

## A cursor menu over the given labels. Returns the chosen index, or -1 when B is pressed.
func _menu(items: Array, cols: int, on_move: Callable = Callable(), allow_back: bool = true) -> int:
	var cursor := UiTheme.label("▶", Vector2.ZERO, 16, Color("d04040"))
	menu_layer.add_child(cursor)
	var i := 0
	while true:
		var it: Label = items[i]
		cursor.global_position = it.global_position + Vector2(-10, 0)
		if on_move.is_valid():
			on_move.call(i)
		await get_tree().process_frame
		var moved := i
		if Input.is_action_just_pressed("move_right") and i % cols < cols - 1 and i + 1 < items.size():
			moved = i + 1
		elif Input.is_action_just_pressed("move_left") and i % cols > 0:
			moved = i - 1
		elif Input.is_action_just_pressed("move_down") and i + cols < items.size():
			moved = i + cols
		elif Input.is_action_just_pressed("move_up") and i - cols >= 0:
			moved = i - cols
		elif Input.is_action_just_pressed("a"):
			cursor.queue_free()
			return i
		elif allow_back and Input.is_action_just_pressed("b"):
			cursor.queue_free()
			return -1
		i = moved
	return -1


func _clear_menu() -> void:
	for n in menu_layer.get_children():
		n.queue_free()


func _choose_action() -> Dictionary:
	while true:
		_clear_menu()
		msg.show_text("What will\n%s do?" % player.display_name(), true)
		var panel := Panel.new()
		panel.position = Vector2(184, 132)
		panel.size = Vector2(132, 44)
		panel.add_theme_stylebox_override("panel", UiTheme.box(Color("fdf6e8"), Color("c05040"), 4))
		menu_layer.add_child(panel)
		var items: Array = []
		var names := ["FIGHT", "BAG", "PKMN", "RUN"]
		for k in 4:
			var l := UiTheme.label(names[k], Vector2(200 + (k % 2) * 62, 134 + (k / 2) * 19))
			menu_layer.add_child(l)
			items.append(l)
		var pick := await _menu(items, 2, Callable(), false)
		_clear_menu()
		match pick:
			0:
				var mv := await _choose_move()
				if mv >= 0:
					return {"kind": "move", "index": mv}
			1:
				var item := await _choose_item()
				if item != "":
					return {"kind": "item", "id": item}
			2:
				var sw := await _choose_party(false)
				if sw >= 0:
					return {"kind": "switch", "index": sw}
			3:
				return {"kind": "run"}
	return {}


func _choose_move() -> int:
	_clear_menu()
	msg.hide()
	var panel := Panel.new()
	panel.position = Vector2(4, 132)
	panel.size = Vector2(312, 44)
	menu_layer.add_child(panel)
	var info := Panel.new()
	info.position = Vector2(226, 132)
	info.size = Vector2(90, 44)
	info.add_theme_stylebox_override("panel", UiTheme.box(Color("eef2f8"), Color("3a4a5a"), 4))
	menu_layer.add_child(info)
	var pp_l := UiTheme.label("", Vector2(234, 134))
	var type_l := UiTheme.label("", Vector2(234, 153))
	menu_layer.add_child(pp_l)
	menu_layer.add_child(type_l)
	var items: Array = []
	for k in 4:
		var text := "-"
		if k < player.moves.size():
			text = Data.moves[player.moves[k]["id"]]["name"]
		var l := UiTheme.label(text, Vector2(18 + (k % 2) * 104, 134 + (k / 2) * 19))
		menu_layer.add_child(l)
		items.append(l)
	items = items.slice(0, max(1, player.moves.size()))
	var on_move := func(i: int):
		if i >= player.moves.size():
			return
		var mv: Dictionary = player.moves[i]
		var md: Dictionary = Data.moves[mv["id"]]
		pp_l.text = "PP %d/%d" % [mv["pp"], md["pp"]]
		type_l.text = String(md["type"]).to_upper()
		type_l.add_theme_color_override("font_color", Data.TYPE_COLORS.get(md["type"], Color.BLACK).darkened(0.35))
	while true:
		var pick := await _menu(items, 2, on_move)
		if pick < 0:
			_clear_menu()
			return -1
		if int(player.moves[pick]["pp"]) <= 0:
			continue
		_clear_menu()
		return pick
	return -1


func _choose_item() -> String:
	_clear_menu()
	var ids: Array = []
	for id in Game.bag:
		if int(Game.bag[id]) > 0:
			ids.append(id)
	if ids.is_empty():
		await _say(["The BAG is empty."])
		return ""
	var panel := Panel.new()
	panel.position = Vector2(184, 132 - 20 * ids.size() + 18)
	panel.size = Vector2(132, 20 * ids.size() + 8)
	menu_layer.add_child(panel)
	var items: Array = []
	for k in ids.size():
		var l := UiTheme.label("%s x%d" % [Data.ITEMS[ids[k]]["name"], Game.bag[ids[k]]], panel.position + Vector2(14, 2 + k * 20))
		menu_layer.add_child(l)
		items.append(l)
	msg.show_text("Use which item?", true)
	var pick := await _menu(items, 1)
	_clear_menu()
	return "" if pick < 0 else ids[pick]


## Party list. Returns the index of the Pokémon to send out, or -1.
func _choose_party(forced: bool) -> int:
	_clear_menu()
	var panel := Panel.new()
	panel.position = Vector2(30, 6)
	panel.size = Vector2(260, 122)
	menu_layer.add_child(panel)
	var items: Array = []
	for k in Game.party.size():
		var m: Mon = Game.party[k]
		var line := "%s  Lv%d  %d/%d%s" % [m.display_name(), m.level, max(m.hp, 0), m.max_hp(), _status_tag(m)]
		if m == player:
			line += "  (in battle)"
		var l := UiTheme.label(line, Vector2(48, 10 + k * 19))
		if m.is_fainted():
			l.add_theme_color_override("font_color", Color("a04040"))
		menu_layer.add_child(l)
		items.append(l)
	msg.show_text("Choose a POKéMON." if forced else "Switch to which POKéMON?", true)
	while true:
		var pick := await _menu(items, 1, Callable(), not forced)
		if pick < 0:
			_clear_menu()
			return -1
		var m: Mon = Game.party[pick]
		if m == player or m.is_fainted():
			continue
		_clear_menu()
		return pick
	return -1


# ------------------------------------------------------------------ turns

func _play_turn(action: Dictionary) -> String:
	msg.show_text("", true)
	match action["kind"]:
		"run":
			await _say(["Got away safely!"])
			return "ran"
		"switch":
			await _switch_to(int(action["index"]))
		"item":
			var r := await _use_item(String(action["id"]))
			if r != "":
				return r
	var enemy_move := _enemy_pick()
	var order: Array = ["enemy"]
	if action["kind"] == "move":
		var pm: String = player.moves[int(action["index"])]["id"]
		var p_first := _goes_first(pm, enemy_move)
		order = [["player", int(action["index"])], ["enemy"]] if p_first else [["enemy"], ["player", int(action["index"])]]
	else:
		order = [["enemy"]]
	for entry in order:
		var side: String = entry[0]
		var user: Mon = player if side == "player" else enemy
		if user.is_fainted():
			continue
		if side == "player":
			await _use_move("player", int(entry[1]))
		else:
			await _use_move_id("enemy", enemy_move)
		var r := await _check_faints()
		if r == "won" or r == "lost":
			return r
		if r == "switched":
			return ""
	for side in ["player", "enemy"]:
		await _end_of_turn(side)
		var r2 := await _check_faints()
		if r2 == "won" or r2 == "lost":
			return r2
	return ""


func _enemy_pick() -> String:
	var usable := enemy.moves.filter(func(m): return int(m["pp"]) > 0)
	if usable.is_empty():
		return "tackle"
	var mv: Dictionary = usable[randi() % usable.size()]
	mv["pp"] = int(mv["pp"]) - 1
	return mv["id"]


func _speed(side: String) -> float:
	var m: Mon = player if side == "player" else enemy
	var s := m.stat("spe") * _stage_mult(stages[side]["spe"])
	if m.status == "par":
		s *= 0.5
	return s


func _goes_first(player_move: String, enemy_move: String) -> bool:
	var pp := 1 if Data.moves[player_move]["effect"].contains("prio") else 0
	var ep := 1 if Data.moves.get(enemy_move, {}).get("effect", "").contains("prio") else 0
	if pp != ep:
		return pp > ep
	var a := _speed("player")
	var b := _speed("enemy")
	return a > b or (a == b and randf() < 0.5)


static func _stage_mult(stage: int) -> float:
	return (2.0 + stage) / 2.0 if stage >= 0 else 2.0 / (2.0 - stage)


func _use_move(side: String, index: int) -> void:
	var mv: Dictionary = player.moves[index]
	mv["pp"] = max(0, int(mv["pp"]) - 1)
	await _use_move_id(side, mv["id"])


func _use_move_id(side: String, move_id: String) -> void:
	var user: Mon = player if side == "player" else enemy
	var foe_side := "enemy" if side == "player" else "player"
	var target: Mon = enemy if side == "player" else player
	var md: Dictionary = Data.moves[move_id]
	var who := _who(side)
	if user.status == "slp":
		user.sleep_turns -= 1
		if user.sleep_turns > 0:
			await _say(["%s is fast asleep." % who])
			return
		user.status = ""
		_refresh_box(side)
		await _say(["%s woke up!" % who])
	if user.status == "par" and randf() < 0.25:
		await _say(["%s is paralyzed! It can't move!" % who])
		return
	await _say(["%s used %s!" % [who, String(md["name"]).to_upper()]])
	var acc := int(md["accuracy"])
	if acc > 0:
		var chance := acc / 100.0 * _stage_mult(stages[side]["acc"] - stages[foe_side]["eva"])
		if randf() > chance:
			await _say(["But it missed!" if md["category"] == "status" else "%s's attack missed!" % who])
			return
	var effects := _parse_effects(String(md["effect"]))
	if md["category"] == "status":
		var did := false
		for e in effects:
			did = await _apply_effect(e, side, foe_side, 0) or did
		if not did:
			await _say(["But nothing happened!"])
		return
	var eff := Data.effectiveness(md["type"], target.types())
	if eff == 0.0:
		await _say(["It doesn't affect %s..." % _who(foe_side).replace("The wild", "the wild")])
		return
	var hits := 1
	for e in effects:
		if e["kind"] == "multi":
			hits = [2, 2, 3, 3, 4, 5][randi() % 6]
	var total := 0
	var landed := 0
	for h in hits:
		if target.is_fainted():
			break
		var crit := randf() < 1.0 / 16.0
		var dmg := _damage(user, target, md, side, foe_side, crit, eff)
		var before := target.hp
		target.hp = max(0, target.hp - dmg)
		total += before - target.hp
		landed += 1
		await _hit_flash(foe_side)
		await _animate_hp(foe_side, before, target.hp)
		if crit:
			await _say(["A critical hit!"])
	if hits > 1:
		await _say(["Hit %d time(s)!" % landed])
	if eff > 1.0:
		await _say(["It's super effective!"])
	elif eff < 1.0:
		await _say(["It's not very effective..."])
	for e in effects:
		if e["kind"] == "drain" and total > 0 and not user.is_fainted():
			var before_u := user.hp
			user.hp = min(user.max_hp(), user.hp + max(1, total / 2))
			await _animate_hp(side, before_u, user.hp)
			await _say(["%s had its energy drained!" % _who(foe_side)])
		elif e["kind"] in ["stat", "status"] and randf() * 100.0 < e["chance"]:
			if e["kind"] == "status" and target.is_fainted():
				continue
			await _apply_effect(e, side, foe_side, total)


func _who(side: String) -> String:
	return player.display_name() if side == "player" else "The wild " + enemy.display_name()


func _damage(user: Mon, target: Mon, md: Dictionary, side: String, foe_side: String, crit: bool, eff: float) -> int:
	var physical: bool = md["category"] == "physical"
	var a_key := "atk" if physical else "spa"
	var d_key := "def" if physical else "spd"
	var a_stage: int = stages[side][a_key]
	var d_stage: int = stages[foe_side][d_key]
	if crit:
		a_stage = max(a_stage, 0)
		d_stage = min(d_stage, 0)
	var a := user.stat(a_key) * _stage_mult(a_stage)
	var d := target.stat(d_key) * _stage_mult(d_stage)
	if physical and user.status == "brn":
		a *= 0.5
	var base: float = floor(floor(floor(2.0 * user.level / 5.0 + 2.0) * float(md["power"]) * a / d) / 50.0) + 2.0
	var mod := eff * (1.5 if crit else 1.0) * randf_range(0.85, 1.0)
	if user.types().has(md["type"]):
		mod *= 1.5
	return max(1, int(base * mod))


## Effects like "t:atk-1", "30%par", "s:spe+2", "drain".
func _parse_effects(s: String) -> Array:
	var out: Array = []
	for raw in s.split(",", false):
		var tok := raw.strip_edges()
		var chance := 100.0
		if tok.contains("%"):
			chance = float(tok.get_slice("%", 0))
			tok = tok.get_slice("%", 1)
		if tok.begins_with("t:") or tok.begins_with("s:"):
			var body := tok.substr(2)
			var sign_at: int = maxi(body.find("+"), body.find("-"))
			out.append({"kind": "stat", "who": tok[0], "stat": body.substr(0, sign_at), "amount": int(body.substr(sign_at)), "chance": chance})
		elif tok in ["par", "brn", "psn", "slp"]:
			out.append({"kind": "status", "status": tok, "chance": chance})
		else:
			out.append({"kind": tok, "chance": chance})
	return out


func _apply_effect(e: Dictionary, side: String, foe_side: String, _dmg: int) -> bool:
	match e["kind"]:
		"stat":
			var tside: String = side if e["who"] == "s" else foe_side
			var key: String = e["stat"]
			var cur: int = stages[tside][key]
			var amount: int = e["amount"]
			var name: String = STAGE_NAMES.get(key, key)
			if (amount > 0 and cur >= 6) or (amount < 0 and cur <= -6):
				await _say(["%s's %s won't go any %s!" % [_who(tside), name, "higher" if amount > 0 else "lower"]])
				return false
			stages[tside][key] = clamp(cur + amount, -6, 6)
			var word := ("rose" if amount > 0 else "fell")
			if abs(amount) >= 2:
				word = "rose sharply" if amount > 0 else "harshly fell"
			await _say(["%s's %s %s!" % [_who(tside), name, word]])
			return true
		"status":
			var target: Mon = enemy if foe_side == "enemy" else player
			var st: String = e["status"]
			var immune := {"par": "Electric", "brn": "Fire", "psn": "Poison"}
			if target.status != "" or target.types().has(immune.get(st, "-")) or (st == "psn" and target.types().has("Steel")):
				if e["chance"] >= 100.0:
					await _say(["But it failed!"])
				return false
			target.status = st
			if st == "slp":
				target.sleep_turns = randi_range(2, 4)
			_refresh_box(foe_side)
			var words := {"par": "is paralyzed! It may be unable to move!", "brn": "was burned!", "psn": "was poisoned!", "slp": "fell asleep!"}
			await _say(["%s %s" % [_who(foe_side), words[st]]])
			return true
		"recover":
			var user: Mon = player if side == "player" else enemy
			if user.hp >= user.max_hp():
				await _say(["%s's HP is full!" % _who(side)])
				return false
			var before := user.hp
			user.hp = min(user.max_hp(), user.hp + user.max_hp() / 2)
			await _animate_hp(side, before, user.hp)
			await _say(["%s regained health!" % _who(side)])
			return true
	return false


func _end_of_turn(side: String) -> void:
	var m: Mon = player if side == "player" else enemy
	if m.is_fainted() or not (m.status in ["brn", "psn"]):
		return
	var before := m.hp
	m.hp = max(0, m.hp - max(1, m.max_hp() / (16 if m.status == "brn" else 8)))
	await _animate_hp(side, before, m.hp)
	await _say(["%s is hurt by its %s!" % [_who(side), "burn" if m.status == "brn" else "poison"]])


func _hit_flash(side: String) -> void:
	var s: TextureRect = enemy_sprite if side == "enemy" else player_sprite
	for i in 3:
		s.visible = false
		await get_tree().create_timer(0.06).timeout
		s.visible = true
		await get_tree().create_timer(0.06).timeout


## Returns "won", "lost", "switched" or "".
func _check_faints() -> String:
	if enemy.is_fainted():
		await _faint_anim(enemy_sprite)
		await _say(["The wild %s fainted!" % enemy.display_name()])
		await _give_exp()
		return "won"
	if player.is_fainted():
		await _faint_anim(player_sprite)
		await _say(["%s fainted!" % player.display_name()])
		if Game.lead() == null:
			await _say(["You have no more POKéMON that can fight!", "You blacked out!"])
			return "lost"
		var pick := await _choose_party(true)
		await _switch_to(pick, true)
		return "switched"
	return ""


func _faint_anim(s: TextureRect) -> void:
	var tw := create_tween().set_parallel()
	tw.tween_property(s, "position:y", s.position.y + 40, 0.35)
	tw.tween_property(s, "modulate:a", 0.0, 0.35)
	await tw.finished
	s.hide()


func _switch_to(index: int, after_faint: bool = false) -> void:
	if not after_faint:
		await _say(["%s, come back!" % player.display_name()])
		var tw := create_tween()
		tw.tween_property(player_sprite, "modulate:a", 0.0, 0.25)
		await tw.finished
	player = Game.party[index]
	stages["player"] = _fresh_stages()
	_show_mon("player")
	await _say(["Go! %s!" % player.display_name()])


func _give_exp() -> void:
	var amount := int(int(enemy.data()["exp_yield"]) * enemy.level / 7.0)
	await _say(["%s gained %d EXP. Points!" % [player.display_name(), amount]])
	var events := player.gain_exp(amount)
	for ev in events:
		_refresh_box("player", true)
		await _say(["%s grew to Lv. %d!" % [player.display_name(), ev["level"]]])
		for mid in ev["learned"]:
			if String(mid).begins_with("!"):
				var name := String(Data.moves[String(mid).substr(1)]["name"]).to_upper()
				await _say(["%s wants to learn %s, but it already knows four moves." % [player.display_name(), name]])
			else:
				await _say(["%s learned %s!" % [player.display_name(), String(Data.moves[mid]["name"]).to_upper()]])
	_refresh_box("player", true)


func _use_item(id: String) -> String:
	Game.bag[id] = int(Game.bag[id]) - 1
	var item: Dictionary = Data.ITEMS[id]
	if item["kind"] == "heal":
		var before := player.hp
		player.hp = min(player.max_hp(), player.hp + int(item["amount"]))
		await _say(["You used a %s." % item["name"]])
		await _animate_hp("player", before, player.hp)
		await _say(["%s's HP was restored." % player.display_name()])
		return ""
	# Poké Ball.
	await _say(["You threw a %s!" % item["name"]])
	var rate := float(enemy.data().get("catch_rate", 190))
	var a := (3.0 * enemy.max_hp() - 2.0 * enemy.hp) * rate * float(item["ball_bonus"]) / (3.0 * enemy.max_hp())
	if enemy.status == "slp":
		a *= 2.0
	elif enemy.status != "":
		a *= 1.5
	var p := clampf(a / 255.0, 0.0, 1.0)
	var shake_p := pow(p, 0.25)
	var tw := create_tween()
	tw.tween_property(enemy_sprite, "modulate", Color(1, 0.3, 0.3, 0.0), 0.3)
	await tw.finished
	var shakes := 0
	for i in 3:
		if randf() > shake_p:
			break
		shakes += 1
		await msg.show_text("." .repeat(i + 1), true)
		await get_tree().create_timer(0.45).timeout
	if shakes == 3 and randf() <= shake_p:
		await _say(["Gotcha! %s was caught!" % enemy.display_name()])
		if Game.party.size() < 6:
			Game.party.append(enemy)
			await _say(["%s was added to your party." % enemy.display_name()])
		else:
			await _say(["%s was sent to the PC. (Boxes come later.)" % enemy.display_name()])
		return "caught"
	var back := create_tween()
	back.tween_property(enemy_sprite, "modulate", Color.WHITE, 0.25)
	await back.finished
	var lines := ["Oh no! The POKéMON broke free!", "Aww! It appeared to be caught!", "Aargh! Almost had it!", "Shoot! It was so close, too!"]
	await _say([lines[shakes]])
	return ""

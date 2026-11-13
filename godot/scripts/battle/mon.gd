class_name Mon
extends RefCounted
## One Pokémon: species, level, stats, moves and current HP.

var species_id: String
var level: int = 1
var exp: int = 0
var ivs: Dictionary = {}
var moves: Array = []  # [{"id": String, "pp": int}]
var hp: int = 1
var status: String = ""  # "", "par", "brn", "psn", "slp"
var sleep_turns: int = 0
var nickname: String = ""

const STATS := ["hp", "atk", "def", "spa", "spd", "spe"]


static func create(sid: String, lvl: int) -> Mon:
	var m := Mon.new()
	m.species_id = sid
	m.level = lvl
	m.exp = exp_for_level(lvl)
	for s in STATS:
		m.ivs[s] = randi_range(0, 31)
	m.moves = []
	for mid in m.moves_at_level(lvl):
		m.moves.append({"id": mid, "pp": int(Data.moves[mid]["pp"])})
	m.hp = m.max_hp()
	return m


func data() -> Dictionary:
	return Data.species[species_id]


func display_name() -> String:
	return nickname if nickname != "" else String(data()["name"]).to_upper()


func types() -> Array:
	return data()["types"]


func stat(key: String) -> int:
	var base := int(data()["base"][key])
	var iv := int(ivs.get(key, 15))
	if key == "hp":
		return int((2 * base + iv) * level / 100.0) + level + 10
	return int((2 * base + iv) * level / 100.0) + 5


func max_hp() -> int:
	return stat("hp")


func is_fainted() -> bool:
	return hp <= 0


## The last four moves learned by this level, like a wild Pokémon in the main games.
func moves_at_level(lvl: int) -> Array:
	var known: Array = []
	for entry in data()["learnset"]:
		var mid: String = entry[1]
		if int(entry[0]) <= lvl and not known.has(mid) and Data.moves.has(mid):
			known.append(mid)
	return known.slice(max(0, known.size() - 4))


static func exp_for_level(lvl: int) -> int:
	return lvl * lvl * lvl  # medium-fast curve


func heal_full() -> void:
	hp = max_hp()
	status = ""
	for m in moves:
		m["pp"] = int(Data.moves[m["id"]]["pp"])


## Adds EXP and returns the list of levels gained, with any new moves learned.
func gain_exp(amount: int) -> Array:
	var events: Array = []
	exp += amount
	while level < 100 and exp >= exp_for_level(level + 1):
		var old_max := max_hp()
		level += 1
		hp += max_hp() - old_max
		var learned: Array = []
		for entry in data()["learnset"]:
			if int(entry[0]) == level:
				var mid: String = entry[1]
				if not Data.moves.has(mid) or moves.any(func(m): return m["id"] == mid):
					continue
				if moves.size() < 4:
					moves.append({"id": mid, "pp": int(Data.moves[mid]["pp"])})
					learned.append(mid)
				else:
					learned.append("!" + mid)  # could not learn, no room yet (move relearn UI comes later)
		events.append({"level": level, "learned": learned})
	return events

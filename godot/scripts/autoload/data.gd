extends Node
## Static game data: species, moves and the type chart. Species come from beryl-design/species.ts
## (converted by tools/convert_design_data.mjs), moves from tools/moves_table.py.

var species: Dictionary = {}
var moves: Dictionary = {}

const TYPES := ["Normal", "Fire", "Water", "Electric", "Grass", "Ice", "Fighting", "Poison", "Ground",
	"Flying", "Psychic", "Bug", "Rock", "Ghost", "Dragon", "Dark", "Steel", "Fairy"]

## CHART[attacking type][defending type] = multiplier. Missing entries are 1.
const CHART := {
	"Normal": {"Rock": 0.5, "Ghost": 0.0, "Steel": 0.5},
	"Fire": {"Fire": 0.5, "Water": 0.5, "Grass": 2.0, "Ice": 2.0, "Bug": 2.0, "Rock": 0.5, "Dragon": 0.5, "Steel": 2.0},
	"Water": {"Fire": 2.0, "Water": 0.5, "Grass": 0.5, "Ground": 2.0, "Rock": 2.0, "Dragon": 0.5},
	"Electric": {"Water": 2.0, "Electric": 0.5, "Grass": 0.5, "Ground": 0.0, "Flying": 2.0, "Dragon": 0.5},
	"Grass": {"Fire": 0.5, "Water": 2.0, "Grass": 0.5, "Poison": 0.5, "Ground": 2.0, "Flying": 0.5, "Bug": 0.5, "Rock": 2.0, "Dragon": 0.5, "Steel": 0.5},
	"Ice": {"Fire": 0.5, "Water": 0.5, "Grass": 2.0, "Ice": 0.5, "Ground": 2.0, "Flying": 2.0, "Dragon": 2.0, "Steel": 0.5},
	"Fighting": {"Normal": 2.0, "Ice": 2.0, "Poison": 0.5, "Flying": 0.5, "Psychic": 0.5, "Bug": 0.5, "Rock": 2.0, "Ghost": 0.0, "Dark": 2.0, "Steel": 2.0, "Fairy": 0.5},
	"Poison": {"Grass": 2.0, "Poison": 0.5, "Ground": 0.5, "Rock": 0.5, "Ghost": 0.5, "Steel": 0.0, "Fairy": 2.0},
	"Ground": {"Fire": 2.0, "Electric": 2.0, "Grass": 0.5, "Poison": 2.0, "Flying": 0.0, "Bug": 0.5, "Rock": 2.0, "Steel": 2.0},
	"Flying": {"Electric": 0.5, "Grass": 2.0, "Fighting": 2.0, "Bug": 2.0, "Rock": 0.5, "Steel": 0.5},
	"Psychic": {"Fighting": 2.0, "Poison": 2.0, "Psychic": 0.5, "Dark": 0.0, "Steel": 0.5},
	"Bug": {"Fire": 0.5, "Grass": 2.0, "Fighting": 0.5, "Poison": 0.5, "Flying": 0.5, "Psychic": 2.0, "Ghost": 0.5, "Dark": 2.0, "Steel": 0.5, "Fairy": 0.5},
	"Rock": {"Fire": 2.0, "Ice": 2.0, "Fighting": 0.5, "Ground": 0.5, "Flying": 2.0, "Bug": 2.0, "Steel": 0.5},
	"Ghost": {"Normal": 0.0, "Psychic": 2.0, "Ghost": 2.0, "Dark": 0.5},
	"Dragon": {"Dragon": 2.0, "Steel": 0.5, "Fairy": 0.0},
	"Dark": {"Fighting": 0.5, "Psychic": 2.0, "Ghost": 2.0, "Dark": 0.5, "Fairy": 0.5},
	"Steel": {"Fire": 0.5, "Water": 0.5, "Electric": 0.5, "Ice": 2.0, "Rock": 2.0, "Steel": 0.5, "Fairy": 2.0},
	"Fairy": {"Fire": 0.5, "Fighting": 2.0, "Poison": 0.5, "Dragon": 2.0, "Dark": 2.0, "Steel": 0.5},
}

const TYPE_COLORS := {
	"Normal": Color("a8a878"), "Fire": Color("f08030"), "Water": Color("6890f0"), "Electric": Color("f8d030"),
	"Grass": Color("78c850"), "Ice": Color("98d8d8"), "Fighting": Color("c03028"), "Poison": Color("a040a0"),
	"Ground": Color("e0c068"), "Flying": Color("a890f0"), "Psychic": Color("f85888"), "Bug": Color("a8b820"),
	"Rock": Color("b8a038"), "Ghost": Color("705898"), "Dragon": Color("7038f8"), "Dark": Color("705848"),
	"Steel": Color("b8b8d0"), "Fairy": Color("ee99ac"),
}

const ITEMS := {
	"pokeball": {"name": "POKé BALL", "kind": "ball", "ball_bonus": 1.0},
	"potion": {"name": "POTION", "kind": "heal", "amount": 20},
}


func _ready() -> void:
	species = _load_json("res://data/species.json")
	moves = _load_json("res://data/moves.json")


func _load_json(path: String) -> Dictionary:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		push_error("Missing data file " + path)
		return {}
	var parsed = JSON.parse_string(f.get_as_text())
	return parsed if parsed is Dictionary else {}


func effectiveness(move_type: String, defender_types: Array) -> float:
	var m := 1.0
	var row: Dictionary = CHART.get(move_type, {})
	for t in defender_types:
		m *= float(row.get(t, 1.0))
	return m


## Back sprite (<dex>_back.png), or null when there is none yet.
func back_sprite(species_id: String) -> Texture2D:
	var dex: String = species.get(species_id, {}).get("dex", "")
	var path := "res://assets/pokemon/back/%s_back.png" % dex
	return load(path) if dex != "" and ResourceLoader.exists(path) else null


## Battle sprite for a species. Front sprites live in assets/pokemon/front.
func front_sprite(species_id: String) -> Texture2D:
	var file = species.get(species_id, {}).get("sprite")
	if file is String and file != "":
		var path: String = "res://assets/pokemon/front/" + file
		if ResourceLoader.exists(path):
			return load(path)
	return load("res://assets/pokemon/missing.png") if ResourceLoader.exists("res://assets/pokemon/missing.png") else null

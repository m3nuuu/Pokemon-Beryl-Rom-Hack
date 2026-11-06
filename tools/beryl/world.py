"""Kaldria: every generated map, on the FireRed (Kanto) tilesets.

    python3 tools/beryl/world.py                 (re)write every map into the repo
    python3 tools/beryl/world.py --render DIR    also save a PNG of each outdoor map

The maps are part of the `make firered` build."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kaldria import Grid, Town, Interior, pokecenter, mart, room, Project, upper_id  # noqa: E402
from mapgen import blk, PALLET, LAVENDER, VERMILION, CELADON  # noqa: E402
import render  # noqa: E402

PROJ = Project()
# Kanto place-name slots reused for Kaldria places (the name shown on entering a map)
MAPSEC_NAMES = {
    'MAPSEC_PALLET_TOWN': 'STILLBROOK',
    'MAPSEC_ROUTE_1': 'ROUTE 1',
    'MAPSEC_ROUTE_2': 'ROUTE 2',
    'MAPSEC_ROUTE_3': 'LETHYS DAM',
    'MAPSEC_ROUTE_4': 'ROUTE 3',
    'MAPSEC_ROUTE_5': 'ROUTE 4',
    'MAPSEC_POKEMON_TOWER': 'LANTERNCROSS',
    'MAPSEC_VERMILION_CITY': 'REEDMOUTH',
    'MAPSEC_CELADON_CITY': 'VALECROWN CITY',
    'MAPSEC_ROUTE_6': 'LETHYS DELTA',
    'MAPSEC_ROUTE_7': 'VALECROWN BEACH',
    'MAPSEC_POWER_PLANT': 'POWER STATION',
}


# ---------------------------------------------------------------- decoration helpers
def picket(g, x0, x1, y):
    """A white picket fence (Pallet tiles) from x0 to x1."""
    for x in range(x0, x1 + 1):
        g.over[(x, y)] = blk(0x290 if x == x0 else 0x288 if x == x1 else 0x287, 1, 0)


def gym_sign(t, x, y, text):
    """The red GYM board on its post, one tile tall object drawn over two tiles."""
    t.grid.over[(x, y - 1)] = blk(0x160, 1, 0)
    t.grid.over[(x, y)] = blk(0x168, 1, 0)
    t.sign(x, y, text, facing='BG_EVENT_PLAYER_FACING_ANY', post=False)


def bush(g, x, y):
    """A round shrub."""
    g.over[(x, y)] = blk(0x005, 1, 0)


WANDER = 'MOVEMENT_TYPE_WANDER_AROUND'


# ---------------------------------------------------------------- Stillbrook
def stillbrook():
    """Beryl's home town, south-west Kaldria. North: the ridge and Cragway Cave.
    East: Route 2 climbs to the Lethys Dam. South: Route 1 to the Pension and Reedmouth."""
    W, H = 48, 44
    g = Grid(W, H)
    # the ridge along the north edge, with the cave mouth
    g.rect(0, 0, W - 1, 4, '^').rect(0, 5, 11, 5, '^').rect(38, 5, W - 1, 6, '^')
    g.put(30, 4, 'C')
    # west forest edge
    g.trees(0, 6, 1, H - 1)
    # main street, the path from the cave and the road south to Route 1
    g.rect(2, 12, W - 1, 13, '=')
    g.rect(30, 5, 31, 11, '=')
    g.rect(20, 14, 21, H - 1, '=')
    # top row: gym, Pokémon Center, a house, mart
    g.trees(12, 6, 13, 9).trees(38, 7, 47, 11)
    g.rect(21, 8, 22, 11, '*').rect(13, 10, 13, 11, '*').rect(25, 12, 25, 12, '=')
    # west lanes
    g.rect(2, 22, 19, 22, '=').rect(2, 32, 19, 32, '=')
    g.rect(6, 21, 6, 21, '=').rect(13, 21, 13, 21, '=').rect(6, 30, 6, 31, '=').rect(13, 30, 13, 31, '=')
    # front gardens with flowers
    g.rect(2, 16, 3, 20, '*').rect(8, 23, 11, 24, '*').rect(15, 23, 18, 24, '*')
    g.rect(2, 25, 3, 29, '*').rect(8, 33, 10, 33, '*')
    # pond and woods in the south-west
    g.rect(3, 35, 12, 38, '~')
    g.trees(0, 39, 13, H - 1).trees(14, 38, 19, H - 1)
    # east lanes
    g.rect(22, 22, 35, 22, '=').rect(25, 21, 25, 21, '=').rect(31, 21, 31, 21, '=')
    g.rect(22, 31, 32, 31, '=').rect(28, 30, 28, 30, '=')
    g.rect(33, 16, 34, 20, '*').rect(23, 24, 24, 27, '*')
    # the Lethys runs past the south-east corner
    for y in range(28, H):
        x0 = max(37, 46 - (y - 28))
        g.rect(x0, y, W - 1, y, '≈')
    g.trees(36, 14, 47, 25).trees(22, 34, 35, H - 1).trees(22, 38, 23, H - 1)
    g.rect(33, 26, 36, 28, '.')

    t = Town('Stillbrook', g, mapsec='MAPSEC_PALLET_TOWN', music='MUS_RG_PALLET', weather='WEATHER_LEAVES')
    gym = t.building('gym', 3, 7, 'Stillbrook_Gym')
    pokecenter(t, 15, 7, 'HEAL_LOCATION_STILLBROOK', PROJ.heal)
    mart(t, 33, 8, ['ITEM_POKE_BALL', 'ITEM_POTION', 'ITEM_ANTIDOTE', 'ITEM_PARALYZE_HEAL', 'ITEM_AWAKENING', 'ITEM_ESCAPE_ROPE'])
    home = t.building('home', 5, 16, 'Stillbrook_BerylsHouse_1F')
    jasper = t.building('home', 24, 16, 'Stillbrook_JaspersHouse')
    t.buildings.append(('mailbox', 4, 19, None))
    t.buildings.append(('mailbox', 23, 19, None))
    t.buildings.append(('mailbox', 17, 19, None))
    t.buildings.append(('mailbox', 17, 28, None))
    picket(g, 7, 12, 25)
    picket(g, 14, 19, 25)
    picket(g, 2, 4, 34)
    picket(g, 26, 31, 32)
    for x, y in ((10, 20), (11, 20), (29, 20), (35, 21), (19, 29), (24, 29), (32, 28)):
        bush(g, x, y)

    gym_sign(t, 10, 11, 'STILLBROOK POKéMON GYM\nLEADER: TORVALD\n\nThe gym is closed while the leader is away.')
    t.sign(19, 14, 'STILLBROOK\nWhere the river slows down.')
    t.sign(8, 21, "BERYL'S HOUSE")
    t.sign(27, 21, "JASPER'S HOUSE")
    t.sign(32, 6, 'CRAGWAY CAVE\nAhead: CRAGMOOR')
    t.sign(26, 30, 'STILLBROOK LIBRARY\nOpen every day. Please be quiet!')
    t.sign(13, 34, 'Please do not feed the POKéMON in the pond.')

    # people about town
    t.npc('OBJ_EVENT_GFX_OLD_MAN_1', 4, 13, "TORVALD's gym has been shut for years. He went off to train in the mountains.")
    t.npc('OBJ_EVENT_GFX_FAT_MAN_FRLG', 26, 13, 'The power line along the river feeds the whole town. When the dam hums, our lights stay on.', move=WANDER, rx=3, ry=1)
    t.npc('OBJ_EVENT_GFX_LITTLE_GIRL_FRLG', 15, 27, "Tag! You're it! ...Hey, wait up!", move=WANDER, rx=3, ry=2)
    t.npc('OBJ_EVENT_GFX_LITTLE_BOY_FRLG', 9, 27, "I'm the fastest kid in STILLBROOK! Nobody can catch me!", move=WANDER, rx=3, ry=2)
    t.npc('OBJ_EVENT_GFX_WOMAN_1_FRLG', 3, 23, 'I water these flowers every morning. The river water makes them grow so tall!', move='MOVEMENT_TYPE_FACE_LEFT')
    t.npc('OBJ_EVENT_GFX_FISHER', 37, 31, 'I fish in the LETHYS every morning. Grandpa says the river remembers every POKéMON that ever swam in it.', move='MOVEMENT_TYPE_FACE_RIGHT')
    t.npc('OBJ_EVENT_GFX_YOUNGSTER_FRLG', 30, 24, "One day I'll go through CRAGWAY CAVE all by myself. Mum says not yet.", move=WANDER, rx=2, ry=1)
    t.npc('OBJ_EVENT_GFX_OLD_WOMAN_FRLG', 15, 33, 'The pond is older than the town. On quiet nights you can hear it sing.', move='MOVEMENT_TYPE_WANDER_LEFT_AND_RIGHT', rx=2)
    t.npc('OBJ_EVENT_GFX_MEOWTH', 18, 21, 'Meow?', move=WANDER, rx=2, ry=1)
    t.npc('OBJ_EVENT_GFX_PIDGEY', 9, 34, 'Pi-pidgey!', move=WANDER, rx=2, ry=0)
    t.npc('OBJ_EVENT_GFX_PSYDUCK', 7, 37, 'Psy...?', move=WANDER, rx=2, ry=1)
    t.npc('OBJ_EVENT_GFX_CLEFAIRY', 29, 26, 'Clefairy!', move=WANDER, rx=2, ry=1)

    # ---- insides
    h1 = Interior('Stillbrook_BerylsHouse_1F', 'PalletTown_PlayersHouse_1F_Frlg',
                  {'MAP_PALLET_TOWN': ('Stillbrook', home), 'MAP_PALLET_TOWN_PLAYERS_HOUSE_2F': ('Stillbrook_BerylsHouse_2F', None)},
                  music='MUS_RG_PALLET')
    h1.npc('OBJ_EVENT_GFX_OLD_WOMAN_FRLG', 8, 4, "GRANDMA: Good morning, dear! Did you sleep well?\n\nDon't go too far without a POKéMON. The tall grass is full of them.", local='LOCALID_BERYLS_GRANDMA')
    h2 = Interior('Stillbrook_BerylsHouse_2F', 'PalletTown_PlayersHouse_2F_Frlg',
                  {'MAP_PALLET_TOWN_PLAYERS_HOUSE_1F': ('Stillbrook_BerylsHouse_1F', None)}, keep_bgs=True)
    j1 = Interior('Stillbrook_JaspersHouse', 'PalletTown_RivalsHouse_Frlg', {'*': ('Stillbrook', jasper)}, keep_bgs=True)
    j1.npc('OBJ_EVENT_GFX_WOMAN_2_FRLG', 10, 6, "ROSALIND: Oh, hello, BERYL! JASPER ran off somewhere again.\n\nI'm off to the PENSION soon. Somebody has to look after all those POKéMON!")
    j1.npc('OBJ_EVENT_GFX_BOY', 4, 4, "JASPER: Hey, BERYL! One day I'll have a POKéMON and we'll battle every day!", move=WANDER, rx=1, ry=1)
    gy = Interior('Stillbrook_Gym', 'PewterCity_Gym_Frlg', {'*': ('Stillbrook', gym)})
    gy.npc('OBJ_EVENT_GFX_GYM_GUY', 7, 12, 'The leader, TORVALD, is away. Come back when he returns!')
    t.interiors += [h1, h2, j1, gy]
    room(t, 'home', 12, 16, 'Stillbrook_House1', 'PalletTown_RivalsHouse_Frlg',
         [('OBJ_EVENT_GFX_MAN', 4, 4, 'Before the dam was built, the LETHYS flooded STILLBROOK every spring. Now it just sits there, quiet.', WANDER)])
    room(t, 'home', 31, 16, 'Stillbrook_House2', 'PalletTown_RivalsHouse_Frlg',
         [('OBJ_EVENT_GFX_WOMAN_3_FRLG', 6, 5, "My husband works at the dam. He says the water's never been this low.", WANDER),
          ('OBJ_EVENT_GFX_LITTLE_GIRL_FRLG', 9, 4, "When I grow up I'm going to be a GYM LEADER like TORVALD!")])
    room(t, 'home', 5, 25, 'Stillbrook_House3', 'PalletTown_RivalsHouse_Frlg',
         [('OBJ_EVENT_GFX_OLD_MAN_2', 7, 4, 'My knees always ache before it rains. Better than any weather forecast!')])
    room(t, 'home', 12, 25, 'Stillbrook_House4', 'PalletTown_RivalsHouse_Frlg',
         [('OBJ_EVENT_GFX_CAMPER_FRLG', 5, 5, 'ROUTE 1 has a PENSION run by JASPER\'s mum. Trainers leave their POKéMON there.', WANDER)])
    room(t, 'home', 24, 7, 'Stillbrook_House5', 'PalletTown_RivalsHouse_Frlg',
         [('OBJ_EVENT_GFX_GENTLEMAN_FRLG', 6, 5, 'I keep an eye on the PokéMON CENTER from my window. The nurse never sleeps!')])
    room(t, 'lab', 25, 26, 'Stillbrook_Library', 'ViridianCity_School_Frlg',
         [('OBJ_EVENT_GFX_WOMAN_2_FRLG', 6, 2, 'Welcome to the library. We have books about every town along the LETHYS.'),
          ('OBJ_EVENT_GFX_LASS_FRLG', 4, 5, 'This book says KALDRIA had no dam a hundred years ago. The river ran free all the way to the sea.')])
    return t


def route1():
    """South of Stillbrook: the Pension and its garden, flower fields, the farm and the windmill.
    The road east goes on to Reedmouth."""
    W, H = 48, 74
    g = Grid(W, H)
    g.trees(0, 0, 1, H - 1).trees(0, H - 2, W - 1, H - 1)
    for y in range(0, 6):
        g.rect(36 + 2 * y, y, W - 1, y, '≈')
    g.trees(40, 6, W - 1, 33).trees(36, 8, 39, 25)
    g.trees(W - 4, 36, W - 1, H - 1)
    g.rect(20, 0, 21, 35, '=')
    g.rect(10, 34, W - 1, 35, '=')
    g.rect(10, 36, 11, 51, '=')
    g.rect(40, 36, 41, 52, '=')
    g.rect(5, 13, 16, 29, '.')
    g.rect(6, 15, 9, 18, '*').rect(12, 22, 15, 25, '*').rect(6, 25, 8, 27, '*')
    g.fence(4, 12, 17, 30, gaps=[(17, 20), (17, 21)])
    g.rect(18, 20, 19, 21, '=')
    g.trees(2, 2, 15, 9)
    g.rect(4, 38, 8, 41, '*').rect(13, 37, 17, 42, '*').rect(24, 44, 31, 47, '*')
    g.rect(22, 54, 37, 69, ',').rect(2, 40, 3, 49, ',').rect(42, 56, 43, 69, ',')
    g.rect(24, 6, 33, 11, ',')
    g.trees(24, 22, 35, 31)
    g.fence(3, 52, 19, 70, gaps=[(10, 52), (11, 52)])
    for y in (61, 63, 65, 67):
        g.rect(5, y, 17, y, ':')
    g.trees(14, 38, 17, 41)
    t = Town('KaldriaRoute1', g, mapsec='MAPSEC_ROUTE_1', music='MUS_RG_ROUTE1', map_type='MAP_TYPE_ROUTE', weather='WEATHER_LEAVES')
    pension = t.building('lab', 22, 14, 'KaldriaRoute1_Pension')
    t.sign(19, 13, 'LETHYS PENSION\nWe look after your POKéMON!')
    t.sign(19, 1, 'ROUTE 1\nNorth: STILLBROOK\nEast: REEDMOUTH')
    t.sign(12, 51, 'BRAMBLE FARM')
    t.sign(42, 52, 'The old windmill')
    t.npc('OBJ_EVENT_GFX_MAN', 14, 58, 'The soil here is good because the river used to flood it. Since the dam, I have to water everything myself.', move=WANDER, rx=2, ry=1)
    t.npc('OBJ_EVENT_GFX_PICNICKER_FRLG', 30, 35, 'The flower fields smell lovely in the morning. The POKéMON in the tall grass think so too!', move=WANDER, rx=2, ry=0)
    t.npc('OBJ_EVENT_GFX_NIDORAN_F', 8, 20, 'Nido!', move=WANDER, rx=2, ry=2)
    t.npc('OBJ_EVENT_GFX_JIGGLYPUFF', 13, 16, 'Jiggly...', move=WANDER, rx=2, ry=2)
    t.npc('OBJ_EVENT_GFX_SLOWPOKE', 10, 27, '...Slow?', move=WANDER, rx=2, ry=1)
    t.npc('OBJ_EVENT_GFX_DODUO', 9, 64, 'Doduo! Doduo!', move=WANDER, rx=3, ry=1)
    p = Interior('KaldriaRoute1_Pension', 'FourIsland_PokemonDayCare_Frlg', {'*': ('KaldriaRoute1', pension)})
    p.npc('OBJ_EVENT_GFX_WOMAN_2_FRLG', 2, 2, "ROSALIND: Welcome to the LETHYS PENSION!\n\nMy son JASPER says he'll be a famous TRAINER one day. Until then, I look after everyone else's POKéMON.")
    t.interiors.append(p)
    room(t, 'home', 8, 55, 'KaldriaRoute1_FarmHouse', 'PalletTown_RivalsHouse_Frlg',
         [('OBJ_EVENT_GFX_WOMAN_3_FRLG', 6, 5, 'Our family has farmed by the LETHYS for five generations. Grandpa says the river used to talk to him.')])
    room(t, 'home', 26, 38, 'KaldriaRoute1_House', 'PalletTown_RivalsHouse_Frlg',
         [('OBJ_EVENT_GFX_OLD_MAN_1', 6, 5, 'Flowers grow best where the water used to reach. Funny how the land remembers.')])
    room(t, 'home', 38, 53, 'KaldriaRoute1_Windmill', 'PalletTown_RivalsHouse_Frlg',
         [('OBJ_EVENT_GFX_HIKER_FRLG', 6, 5, "The windmill hasn't turned in years. The dam makes all the power now.")])
    return t


def route2():
    """From Stillbrook's main street up the hillside to the west end of the dam."""
    W, H = 28, 30
    g = Grid(W, H)
    g.rect(0, 0, W - 1, 11, '^').rect(0, 12, 5, 21, '^').rect(22, 12, W - 1, 17, '^')
    g.rect(0, 20, W - 1, 21, '^').put(10, 20, 'SS').put(10, 21, 'SS')
    g.rect(8, 18, W - 1, 19, '=').rect(10, 18, 11, 19, '=')
    g.trees(0, 22, 3, 27).trees(16, 26, W - 1, H - 1).trees(6, 12, 9, 15).trees(18, 12, 21, 15)
    g.rect(14, 22, 25, 25, ',').rect(12, 12, 17, 16, ',')
    g.rect(0, 28, 11, 29, '=').rect(10, 22, 11, 27, '=')
    t = Town('KaldriaRoute2', g, mapsec='MAPSEC_ROUTE_2', music='MUS_RG_ROUTE1', map_type='MAP_TYPE_ROUTE')
    t.sign(12, 27, 'ROUTE 2\nUp: LETHYS DAM\nWest: STILLBROOK')
    t.npc('OBJ_EVENT_GFX_HIKER_FRLG', 16, 18, 'From up here you can hear the dam humming. All that water, held back by one wall!', move='MOVEMENT_TYPE_FACE_RIGHT')
    return t


def dam():
    """The Lethys Dam: Mirrormere above, the crest road across, the spillway falling to the river below."""
    W, H = 56, 20
    g = Grid(W, H)
    g.rect(0, 0, W - 1, 5, '≈')
    g.rect(0, 6, W - 1, 7, 'p')                # the crest road
    g.rect(0, 8, W - 1, 13, '^')               # the wall
    g.rect(24, 8, 31, 13, 'W')                 # spillway
    for y in range(14, H):
        a = 22 - (y - 14) // 2
        g.rect(a, y, 55 - a - 2, y, '≈')
    g.trees(0, 14, 15, H - 1).trees(40, 14, W - 1, H - 1)
    t = Town('LethysDam', g, mapsec='MAPSEC_ROUTE_3', music='MUS_RG_ROUTE24', map_type='MAP_TYPE_ROUTE')
    t.npc('OBJ_EVENT_GFX_WORKER_M', 30, 6, 'LETHYS DAM: the power for all of KALDRIA. Please stay on the walkway.', move='MOVEMENT_TYPE_WANDER_LEFT_AND_RIGHT', rx=4)
    return t


def route3():
    """Below the dam: the Lethys runs south-west past Stillbrook; the Lowbank Ruins; the road
    from the power station side to the Lanterncross Temple and the capital."""
    W, H = 84, 36
    g = Grid(W, H)
    for y in range(H):
        cx = max(8, 56 - y * 3.4)
        g.rect(0 if y >= 14 else int(cx - 8), y, int(cx + 7), y, '≈')
    g.trees(0, 0, 25, 11)
    g.trees(66, 0, W - 1, 3).trees(74, 4, W - 1, 21)
    g.rect(52, 6, 70, 17, 'p')
    for x0, y0, x1, y1 in ((52, 6, 55, 8), (60, 6, 63, 7), (67, 9, 70, 11), (52, 14, 53, 17), (64, 14, 66, 15)):
        g.rect(x0, y0, x1, y1, '^')
    g.rect(58, 9, 62, 12, '^').put(60, 12, 'C')
    g.rect(22, 26, W - 1, 27, '=')
    g.rect(22, 28, 23, H - 1, '=')
    g.rect(62, 18, 63, 25, '=')
    g.rect(70, 28, 71, H - 1, '=')
    g.rect(30, 20, 44, 24, ',').rect(46, 29, 60, 33, ',')
    g.trees(26, 30, 43, H - 1).trees(74, 28, W - 1, H - 1).trees(30, 12, 47, 17)
    t = Town('KaldriaRoute3', g, mapsec='MAPSEC_ROUTE_4', music='MUS_RG_ROUTE3', map_type='MAP_TYPE_ROUTE')
    t.sign(64, 18, 'LOWBANK RUINS\nA village that stood here before the dam.')
    t.sign(24, 28, 'South: LANTERNCROSS TEMPLE')
    t.sign(72, 28, 'South: VALECROWN CITY')
    t.npc('OBJ_EVENT_GFX_FISHER', 40, 25, 'People say the old village of LOWBANK is still down there, under the lake. These ruins are all that was left above water.', move='MOVEMENT_TYPE_FACE_LEFT')
    t.npc('OBJ_EVENT_GFX_SCIENTIST', 57, 14, 'These walls are older than the dam, older than STILLBROOK even. Who built them?', move=WANDER, rx=2, ry=1)
    return t


def route4():
    """East of the dam: the power station on the high ground, the one-way drop below it,
    and the long road south to the capital."""
    W, H = 40, 66
    g = Grid(W, H)
    g.trees(0, 0, 9, 15).trees(W - 2, 0, W - 1, H - 1)
    g.rect(0, 0, 1, 17, '^')
    g.rect(0, 18, 31, 19, '=')
    g.rect(32, 0, 33, 29, '=')
    g.rect(0, 20, W - 3, 22, '^').rect(0, 23, 3, 29, '^')
    g.rect(32, 21, 33, 21, '_')
    g.rect(32, 20, 33, 20, '=').rect(32, 22, 33, 22, '=')
    g.rect(14, 30, 33, 31, '=').rect(14, 32, 15, H - 1, '=')
    g.rect(0, 56, 13, 57, '=')
    g.trees(0, 30, 11, 53).trees(18, 34, 35, 63).trees(0, 60, 11, H - 1)
    g.rect(4, 32, 11, 50, ',').rect(18, 24, 29, 28, ',')
    g.rect(16, 13, 18, 17, '=')
    t = Town('KaldriaRoute4', g, secondary=LAVENDER, mapsec='MAPSEC_ROUTE_5', music='MUS_RG_ROUTE24', map_type='MAP_TYPE_ROUTE')
    station = t.building('power_plant', 12, 6, 'KaldriaRoute4_PowerStation')
    t.sign(31, 17, 'LETHYS POWER STATION')
    t.sign(16, 33, 'ROUTE 4\nSouth: VALECROWN CITY\nNorth: WEIRHAVEN')
    ps = Interior('KaldriaRoute4_PowerStation', 'PowerPlant_Frlg', {'*': ('KaldriaRoute4', station)}, mapsec='MAPSEC_POWER_PLANT')
    ps.warps = [w for w in ps.warps if w['y'] > 30]
    ps.npc('OBJ_EVENT_GFX_SCIENTIST', 5, 34, "Every light in VALECROWN runs on the water going through those turbines. If the dam stopped, the capital would go dark.")
    t.interiors.append(ps)
    return t


def vbridge(g, x, y0, y1):
    """A north-south wooden bridge, 3 planks wide, over water from y0 to y1."""
    for y in range(y0, y1 + 1):
        for i, m in enumerate((0x1C5, 0x1C6, 0x1C7)):
            g.over[(x + i, y)] = blk(m, 0, 3)


def lanterncross():
    """The Lanterncross Temple, built into the hillside. The road from Route 3 enters the north gate
    onto the temple's upper hall, goes down the stairs and out of the main doors, then crosses the
    Lethys to Reedmouth. LEADER ODA keeps her gym in the upper hall."""
    W, H = 52, 20
    g = Grid(W, H)
    for y in range(H):
        a = 0 if y < 6 else int((y - 6) * 1.5)
        g.rect(a, y, a + 15, y, '≈')
    g.rect(16, 0, 21, 6, '.')
    g.rect(20, 0, 25, 0, '.').rect(22, 0, 23, 5, '=').rect(18, 5, 34, 6, '=')
    g.trees(24, 0, 25, 1).trees(36, 0, 51, 3)
    g.rect(16, 7, 51, 8, '^')
    g.rect(22, 15, 40, 16, '=').rect(30, 17, 31, 17, '=')
    g.trees(20, 9, 23, 13).trees(38, 9, 41, 13)
    g.trees(44, 9, 51, 11).rect(43, 12, 51, 19, '.').rect(45, 14, 49, 17, '*').trees(46, 18, 51, 19)
    vbridge(g, 29, 17, H - 1)
    t = Town('Lanterncross', g, secondary=LAVENDER, mapsec='MAPSEC_POKEMON_TOWER', music='MUS_RG_LAVENDER', map_type='MAP_TYPE_TOWN')
    gate = t.building('gate', 27, 1, 'Lanterncross_Temple2F')
    hall = t.building('tower', 27, 8, 'Lanterncross_Temple')
    t.sign(26, 5, 'LANTERNCROSS TEMPLE\nNorth gate')
    t.sign(33, 15, 'LANTERNCROSS TEMPLE\nThe lanterns are lit for those the river has taken.')
    t.npc('OBJ_EVENT_GFX_CHANNELER', 35, 16, 'Every year we float lanterns down the LETHYS. The river carries our thoughts to the ones we lost.')
    t.npc('OBJ_EVENT_GFX_OLD_WOMAN_FRLG', 46, 13, 'The park is the quietest place near the capital. Even the POKéMON whisper here.', move=WANDER, rx=2, ry=1)
    # upper hall (gym floor): its stairs up lead out of the north gate, its stairs down to the main hall
    t2 = Interior('Lanterncross_Temple2F', 'PokemonTower_2F_Frlg', {
        'MAP_POKEMON_TOWER_3F': ('Lanterncross', gate), 'MAP_POKEMON_TOWER_1F': ('Lanterncross_Temple', None)})
    t2.npc('OBJ_EVENT_GFX_CHANNELER', 6, 6, "LEADER ODA trains her ghosts up here. She isn't receiving challengers yet.")
    tp = Interior('Lanterncross_Temple', 'PokemonTower_1F_Frlg', {
        '*': ('Lanterncross', hall), 'MAP_POKEMON_TOWER_2F': ('Lanterncross_Temple2F', None)})
    tp.npc('OBJ_EVENT_GFX_CHANNELER', 12, 10, 'Welcome to the LANTERNCROSS TEMPLE. The road from the north gate comes down those stairs. Please walk quietly.')
    t.interiors += [tp, t2]
    return t


def reedmouth():
    """Where the Lethys meets the sea: Grass gym, harbour, and the underpass to the capital."""
    W, H = 52, 36
    g = Grid(W, H)
    g.rect(0, 0, W - 1, H - 1, 'b')
    for y in range(H):
        a = min(36, 21 + int(y * 1.5))
        g.rect(a, y, W - 1, y, '≈')
    g.rect(0, 30, 35, H - 1, '≈')
    vbridge(g, 30, 0, 6)
    g.trees(0, 0, 19, 3).trees(0, 10, 1, 27)
    g.rect(0, 8, 33, 9, 'p').rect(30, 7, 32, 9, 'p').rect(18, 10, 19, 27, 'p').rect(2, 26, 33, 27, 'p')
    g.rect(31, 10, 32, 17, 'p')
    g.rect(22, 0, 28, 6, '.').trees(22, 0, 27, 3)
    t = Town('Reedmouth', g, secondary=VERMILION, mapsec='MAPSEC_VERMILION_CITY', music='MUS_RG_VERMILLION', map_type='MAP_TYPE_CITY')
    pokecenter(t, 4, 3, 'HEAL_LOCATION_REEDMOUTH', PROJ.heal)
    mart(t, 12, 4, ['ITEM_POKE_BALL', 'ITEM_GREAT_BALL', 'ITEM_POTION', 'ITEM_SUPER_POTION', 'ITEM_ANTIDOTE', 'ITEM_PARALYZE_HEAL', 'ITEM_REPEL'])
    gym = t.building('gym', 6, 14, 'Reedmouth_Gym')
    under = t.building('gate', 29, 18, 'Reedmouth_Underpass')
    gym_sign(t, 13, 18, 'REEDMOUTH POKéMON GYM\nLEADER: SEDGE\nRooted in the delta!')
    t.sign(28, 21, 'UNDERPASS\nUnder the LETHYS to VALECROWN CITY', facing='BG_EVENT_PLAYER_FACING_ANY')
    t.sign(1, 7, 'REEDMOUTH\nThe river ends, the sea begins.')
    t.npc('OBJ_EVENT_GFX_SAILOR_FRLG', 12, 28, 'The harbour ferry runs up the LETHYS when the water is high enough. These days it hardly ever is.', move='MOVEMENT_TYPE_WANDER_LEFT_AND_RIGHT', rx=3)
    t.npc('OBJ_EVENT_GFX_FISHER', 30, 28, 'Fresh water meets salt water right here. You can catch all sorts!')
    t.npc('OBJ_EVENT_GFX_LASS_FRLG', 16, 12, 'SEDGE says the reeds clean the river before it reaches the sea.', move=WANDER, rx=1, ry=1)
    t.npc('OBJ_EVENT_GFX_SEEL', 8, 29, 'Seel!', move=WANDER, rx=2, ry=0)
    gy = Interior('Reedmouth_Gym', 'CeladonCity_Gym_Frlg', {'*': ('Reedmouth', gym)})
    gy.npc('OBJ_EVENT_GFX_GYM_GUY', 5, 15, "SEDGE isn't taking challengers yet. Come back later!")
    up = Interior('Reedmouth_Underpass', 'UndergroundPath_NorthEntrance_Frlg', {
        '*': ('Reedmouth', under), 'MAP_UNDERGROUND_PATH_NORTH_SOUTH_TUNNEL': ('Valecrown_Underpass', 3)})
    up.npc('OBJ_EVENT_GFX_POLICEMAN', 9, 6, 'The underpass runs right under the LETHYS. Down the stairs for VALECROWN CITY.')
    t.interiors += [gy, up]
    room(t, 'verm_house', 22, 13, 'Reedmouth_House1', 'VermilionCity_House1_Frlg',
         [('OBJ_EVENT_GFX_WOMAN_3_FRLG', 4, 4, 'My husband works on the boats. When the dam lets more water through, the whole harbour cheers.')])
    room(t, 'verm_hall', 22, 21, 'Reedmouth_Harbour', 'VermilionCity_PokemonFanClub_Frlg',
         [('OBJ_EVENT_GFX_SAILOR_FRLG', 5, 4, 'HARBOUR OFFICE. No ferries today, sorry. The river is too low.')])
    room(t, 'verm_house', 2, 20, 'Reedmouth_House2', 'VermilionCity_House2_Frlg',
         [('OBJ_EVENT_GFX_OLD_MAN_1', 4, 4, 'When I was a boy, the delta flooded every year and the fish came right up to our doors.')])
    return t


def valecrown():
    """VALECROWN CITY, the capital, across the river from Reedmouth."""
    W, H = 72, 60
    g = Grid(W, H)
    g.rect(0, 0, 3, H - 1, '≈').rect(0, 52, W - 1, H - 1, 'b')
    g.trees(4, 0, 15, 5).trees(22, 0, 43, 3).trees(50, 0, W - 1, 3).trees(W - 2, 4, W - 1, 51)
    g.rect(18, 0, 19, 51, 'p').rect(46, 0, 47, 51, 'p')
    g.rect(6, 10, 67, 11, 'p').rect(6, 26, 67, 27, 'p').rect(6, 42, 67, 43, 'p')
    g.rect(6, 12, 7, 41, 'p').rect(32, 12, 33, 49, 'p').rect(60, 12, 61, 41, 'p')
    g.rect(49, 29, 66, 39, ',')
    g.fence(48, 28, 67, 40, gaps=[(57, 28), (58, 28)])
    g.rect(49, 48, 56, 49, '*').rect(54, 44, 56, 47, '*')
    g.rect(36, 36, 43, 39, '~')
    g.trees(8, 12, 15, 19).trees(50, 12, 57, 19).trees(36, 12, 43, 15).trees(22, 30, 29, 33).trees(8, 30, 15, 35)
    g.rect(20, 46, 31, 49, '*')
    g.trees(4, 46, 15, 51).trees(52, 46, 67, 51)
    t = Town('Valecrown', g, secondary=CELADON, mapsec='MAPSEC_CELADON_CITY', music='MUS_RG_CELADON', map_type='MAP_TYPE_CITY')
    gym = t.building('gym', 22, 15, 'Valecrown_Gym')
    pokecenter(t, 10, 5, 'HEAL_LOCATION_VALECROWN', PROJ.heal)
    mart(t, 36, 6, ['ITEM_POKE_BALL', 'ITEM_GREAT_BALL', 'ITEM_ULTRA_BALL', 'ITEM_SUPER_POTION', 'ITEM_HYPER_POTION', 'ITEM_REVIVE', 'ITEM_FULL_HEAL', 'ITEM_SUPER_REPEL'])
    under = t.building('gate', 8, 37, 'Valecrown_Underpass')
    gym_sign(t, 29, 19, 'VALECROWN POKéMON GYM\nLEADER: CASSIAN\nThe spark of the capital!')
    t.sign(20, 12, 'VALECROWN CITY\nThe crown of the valley.')
    t.sign(56, 27, 'VALECROWN ZOO\nMeet the POKéMON of KALDRIA!', facing='BG_EVENT_PLAYER_FACING_ANY')
    t.sign(12, 41, 'UNDERPASS\nTo REEDMOUTH', facing='BG_EVENT_PLAYER_FACING_ANY')
    t.npc('OBJ_EVENT_GFX_GENTLEMAN_FRLG', 30, 12, 'The capital never sleeps. All those lights, all that power, straight from the LETHYS DAM.', move=WANDER, rx=2, ry=1)
    t.npc('OBJ_EVENT_GFX_LITTLE_BOY_FRLG', 44, 28, 'The zoo has a POKéMON from every corner of KALDRIA!', move=WANDER, rx=1, ry=1)
    t.npc('OBJ_EVENT_GFX_POLICEMAN', 46, 45, 'South of here is VALECROWN BEACH. Swim safely!')
    t.npc('OBJ_EVENT_GFX_CUBONE', 52, 33, 'Cubone...', move=WANDER, rx=3, ry=2)
    t.npc('OBJ_EVENT_GFX_MACHOP', 62, 36, 'Machop!', move=WANDER, rx=2, ry=2)
    t.npc('OBJ_EVENT_GFX_NIDORAN_M', 56, 31, 'Nido nido!', move=WANDER, rx=2, ry=2)
    t.npc('OBJ_EVENT_GFX_BEAUTY_FRLG', 40, 44, 'Shopping, shopping, shopping! This city has everything.', move=WANDER, rx=3, ry=0)
    t.npc('OBJ_EVENT_GFX_WORKER_M', 26, 27, 'They keep building and building. Every new tower needs more power from the dam.', move='MOVEMENT_TYPE_WANDER_LEFT_AND_RIGHT', rx=3)
    gy = Interior('Valecrown_Gym', 'ViridianCity_Gym_Frlg', {'*': ('Valecrown', gym)})
    gy.npc('OBJ_EVENT_GFX_GYM_GUY', 14, 20, "CASSIAN is busy keeping the city lights on. Come back later!")
    vu = Interior('Valecrown_Underpass', 'UndergroundPath_SouthEntrance_Frlg', {
        '*': ('Valecrown', under), 'MAP_UNDERGROUND_PATH_NORTH_SOUTH_TUNNEL': ('Reedmouth_Underpass', 3)})
    vu.npc('OBJ_EVENT_GFX_POLICEMAN', 9, 6, 'Down the stairs and under the river for REEDMOUTH.')
    t.interiors += [gy, vu]
    room(t, 'dept_store', 50, 0, 'Valecrown_ShoppingCentre', 'CeladonCity_DepartmentStore_1F_Frlg',
         [('OBJ_EVENT_GFX_WORKER_F', 6, 10, 'Welcome to the VALECROWN SHOPPING CENTRE! The upper floors are still being built.')])
    room(t, 'casino', 36, 29, 'Valecrown_Casino', 'CeladonCity_GameCorner_Frlg',
         [('OBJ_EVENT_GFX_BALDING_MAN', 1, 6, 'The slots are switched off until the new power line is finished. Rotten luck!')])
    room(t, 'prize', 43, 30, 'Valecrown_PrizeHouse', 'CeladonCity_GameCorner_PrizeRoom_Frlg',
         [('OBJ_EVENT_GFX_CLERK', 4, 2, 'Prizes will be handed out once the CASINO opens again.')])
    room(t, 'apartment', 22, 5, 'Valecrown_RadioTower', 'CeladonCity_House1_Frlg',
         [('OBJ_EVENT_GFX_WORKER_M', 4, 4, "KALDRIA FM! Today's news: water levels at the dam are lower than ever.")])
    room(t, 'apartment', 50, 21, 'Valecrown_BikeShop', 'CeruleanCity_BikeShop_Frlg',
         [('OBJ_EVENT_GFX_MAN', 9, 3, 'Bikes! Fresh from the factory! ...Well, they will be, once the factory gets its power back.')])
    room(t, 'apartment', 50, 43, 'Valecrown_FlowerShop', 'CeladonCity_House1_Frlg',
         [('OBJ_EVENT_GFX_WOMAN_1_FRLG', 4, 4, 'Our flowers come from the fields along ROUTE 1. The soil there is the best in KALDRIA.')])
    texts = ['I moved here from STILLBROOK for work. I miss the quiet, but not the floods.',
             "VALECROWN uses more power than every other town put together. Somebody has to pay for it.",
             'Did you see the zoo? My favourite is the POKéMON that lives in the reeds.',
             "The Flowkeepers held a march here last week. They want the river set free.",
             'From the top of the RADIO TOWER you can see the dam on a clear day.',
             'CASSIAN, our gym leader, keeps the city lights on during storms. What a guy!']
    spots = [(10, 21), (22, 37), (62, 21), (24, 21), (36, 21), (62, 5)]
    tpls = ['CeladonCity_House1_Frlg', 'CeruleanCity_House1_Frlg', 'CeruleanCity_House2_Frlg',
            'CeruleanCity_House3_Frlg', 'SaffronCity_House_Frlg', 'FuchsiaCity_House1_Frlg']
    gfx = ['OBJ_EVENT_GFX_WOMAN_2_FRLG', 'OBJ_EVENT_GFX_MAN', 'OBJ_EVENT_GFX_LASS_FRLG', 'OBJ_EVENT_GFX_ROCKER',
           'OBJ_EVENT_GFX_OLD_MAN_1', 'OBJ_EVENT_GFX_COOLTRAINER_M']
    for i, ((x, y), text) in enumerate(zip(spots, texts)):
        room(t, 'apartment', x, y, f'Valecrown_House{i + 1}', tpls[i], [(gfx[i], 4, 4, text, WANDER)])
    return t


def delta():
    """The mouth of the Lethys."""
    W, H = 52, 18
    g = Grid(W, H, '≈')
    g.rect(0, 0, 11, 3, 'b').trees(0, 0, 5, 1).rect(14, 6, 22, 8, 'b').rect(34, 10, 41, 12, 'b')
    t = Town('LethysDelta', g, secondary=VERMILION, mapsec='MAPSEC_ROUTE_6', music='MUS_RG_ROUTE11', map_type='MAP_TYPE_ROUTE')
    t.npc('OBJ_EVENT_GFX_FISHER', 18, 7, 'The LETHYS DELTA. Everything the river carries ends up here.')
    return t


def beach():
    """Valecrown Beach, south of the capital."""
    W, H = 72, 14
    g = Grid(W, H, '≈')
    g.rect(0, 0, W - 1, 5, 'b').rect(20, 6, 40, 6, 'b')
    t = Town('ValecrownBeach', g, secondary=VERMILION, mapsec='MAPSEC_ROUTE_7', music='MUS_RG_ROUTE11', map_type='MAP_TYPE_ROUTE')
    t.npc('OBJ_EVENT_GFX_TUBER_F_FRLG', 30, 3, 'The sea is so warm today!', move=WANDER, rx=3, ry=1)
    t.npc('OBJ_EVENT_GFX_SWIMMER_M_WATER', 50, 9, 'Beyond the beach there is nothing but sea. Kaldria is all there is!', move=WANDER, rx=3, ry=2)
    return t


# Where each outdoor map sits in the world, in tiles (see docs/beryl/WORLD_MAP.md).
WORLD = {
    'Stillbrook': (0, 136),
    'KaldriaRoute1': (0, 180),
    'KaldriaRoute2': (48, 120),
    'LethysDam': (76, 130),
    'KaldriaRoute3': (48, 150),
    'KaldriaRoute4': (132, 120),
    'Lanterncross': (48, 186),
    'Reedmouth': (48, 206),
    'Valecrown': (100, 186),
    'LethysDelta': (48, 242),
    'ValecrownBeach': (100, 246),
}


def link(towns):
    """Connect every pair of outdoor maps that share an edge."""
    pos = {t.name: (WORLD[t.name], t.grid.w, t.grid.h) for t in towns if t.name in WORLD}
    for a in towns:
        if a.name not in pos:
            continue
        (ax, ay), aw, ah = pos[a.name]
        for b in towns:
            if b is a or b.name not in pos:
                continue
            (bx, by), bw, bh = pos[b.name]
            if by + bh == ay and bx < ax + aw and ax < bx + bw:
                a.connect('up', b.name, bx - ax)
            if ay + ah == by and bx < ax + aw and ax < bx + bw:
                a.connect('down', b.name, bx - ax)
            if bx + bw == ax and by < ay + ah and ay < by + bh:
                a.connect('left', b.name, by - ay)
            if ax + aw == bx and by < ay + ah and ay < by + bh:
                a.connect('right', b.name, by - ay)


def resolve_doors(towns):
    """An interior exit marked 'auto' goes to the outdoor door that leads into that interior."""
    outdoor = {t.id: t for t in towns}
    for t in towns:
        for it in t.interiors:
            for w in it.warps:
                if w['dest_warp_id'] == 'auto':
                    dest = outdoor[w['dest_map']]
                    w['dest_warp_id'] = str(next(i for i, d in enumerate(dest.warps) if d['dest_map'] == it.id))


def main():
    towns = [stillbrook(), route1(), route2(), dam(), route3(), route4(), lanterncross(), reedmouth(), valecrown(), delta(), beach()]
    link(towns)
    resolve_doors(towns)
    PROJ.mapsec_names.update(MAPSEC_NAMES)
    for t in towns:
        t.add_to(PROJ)
    PROJ.write()
    if '--render' in sys.argv:
        out = sys.argv[sys.argv.index('--render') + 1]
        os.makedirs(out, exist_ok=True)
        lays = render.layouts()
        for t in towns:
            render.render(lays[t.layout_id], grid='--grid' in sys.argv).save(os.path.join(out, t.name + '.png'))


if __name__ == '__main__':
    main()

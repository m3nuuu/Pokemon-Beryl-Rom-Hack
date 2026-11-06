"""Kaldria: every generated map, on the FireRed (Kanto) tilesets.

    python3 tools/beryl/world.py                 (re)write every map into the repo
    python3 tools/beryl/world.py --render DIR    also save a PNG of each outdoor map and world.png

The south of Kaldria is drawn as one canvas (tools/beryl/canvas.py) after Manuel's region map,
one map tile for every 8 pixels of the drawing, and then cut into maps. Coordinates below are
canvas coordinates: x as in the drawing, y = drawing y + 20.
The maps are part of the `make firered` build."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kaldria import Interior, pokecenter, mart, room, Project  # noqa: E402
from mapgen import blk, stamp, STILLBROOK, LAVENDER, VERMILION, CELADON  # noqa: E402
from canvas import Canvas, Place  # noqa: E402
import render  # noqa: E402

PROJ = Project()
# Kanto place-name slots reused for Kaldria places (the name shown on entering a map)
MAPSEC_NAMES = {
    'MAPSEC_PALLET_TOWN': 'STILLBROOK',
    'MAPSEC_ROUTE_1': 'ROUTE 1',
    'MAPSEC_ROUTE_2': 'ROUTE 2',
    'MAPSEC_ROUTE_3': 'LETHYS DAM',
    'MAPSEC_ROUTE_4': 'LOWBANK RUINS',
    'MAPSEC_ROUTE_5': 'ROUTE 4',
    'MAPSEC_POKEMON_TOWER': 'LANTERNCROSS',
    'MAPSEC_VERMILION_CITY': 'REEDMOUTH',
    'MAPSEC_CELADON_CITY': 'VALECROWN CITY',
    'MAPSEC_ROUTE_6': 'LETHYS DELTA',
    'MAPSEC_ROUTE_7': 'VALECROWN BEACH',
    'MAPSEC_POWER_PLANT': 'POWER STATION',
}

# the big two-door gatehouse of the Saffron gates (primary tiles): its back wall row, where you
# walk in from the north, and the front with the doors
stamp('gate_back', 'LAYOUT_ROUTE5', 22, 32, 6, 1)
stamp('gatehouse', 'LAYOUT_SAFFRON_CITY', 32, 0, 6, 7, (2, 5))
# Vermilion's big brown-roofed gym (primary tiles)
stamp('gym_brown', 'LAYOUT_VERMILION_CITY', 11, 21, 7, 5, (3, 4))

WANDER = 'MOVEMENT_TYPE_WANDER_AROUND'
W, H = 212, 166


# ---------------------------------------------------------------- decoration helpers
def picket(c, x0, x1, y):
    """A white picket fence (Pallet tiles) from x0 to x1."""
    for x in range(x0, x1 + 1):
        c.over[(x, y)] = blk(0x290 if x == x0 else 0x288 if x == x1 else 0x287, 1, 0)


def gym_sign(t, x, y, text):
    """The red GYM board on its post, one object drawn over two tiles."""
    t.canvas.over[(x, y - 1)] = blk(0x160, 1, 0)
    t.canvas.over[(x, y)] = blk(0x168, 1, 0)
    t.sign(x, y, text, facing='BG_EVENT_PLAYER_FACING_ANY', post=False)


def bush(c, x, y):
    c.over[(x, y)] = blk(0x005, 1, 0)


def vbridge(c, x, y0, y1):
    """A north-south wooden bridge, 3 planks wide (x..x+2), over water from y0 to y1."""
    for y in range(y0, y1 + 1):
        for i, m in enumerate((0x1C5, 0x1C6, 0x1C7)):
            c.over[(x + i, y)] = blk(m, 0, 3)


# ---------------------------------------------------------------- the land itself
def terrain(c):
    T = 'T'
    # north: forest over the mountains (the northern maps come later)
    c.rect(0, 0, 97, 27, T)
    # the ridge behind Stillbrook, with the mouth of Cragway Cave
    c.rect(0, 28, 57, 36, '^').rect(0, 28, 11, 37, '^').rect(44, 28, 57, 37, '^')
    c.put(37, 36, 'C')
    # Route 2: shelves stepping up north-east from Stillbrook to the dam, cliffs between them
    c.rect(56, 14, 97, 49, '^')
    c.rect(48, 38, 63, 49, '.')            # A, open to Stillbrook
    c.rect(60, 30, 75, 35, ',')            # B
    c.rect(72, 22, 87, 27, ',')            # C
    c.rect(84, 14, 97, 19, '.')            # D, level with the dam
    c.rect(64, 31, 71, 35, ',').rect(76, 23, 83, 27, ',')
    c.rect(62, 36, 63, 37, 'S').rect(74, 28, 75, 29, 'S').rect(86, 20, 87, 21, 'S')
    c.road([(52, 46), (52, 40), (62, 40), (62, 38)])
    c.road([(62, 34), (62, 32), (74, 32), (74, 30)])
    c.road([(74, 26), (74, 24), (86, 24), (86, 22)])
    c.road([(86, 18), (88, 18)])
    # Mirrormere, held back by the Lethys Dam; the spillway falls into the river basin
    c.rect(98, 0, 157, 17, '~')
    c.rect(84, 18, 165, 19, 'p')           # the crest road
    c.rect(96, 20, 159, 25, '^')           # the wall
    c.rect(124, 20, 131, 25, 'W')          # spillway
    # the plateau of the power station, its cliff, and the one-way drop at the east end
    c.rect(158, 0, 211, 17, '.').rect(158, 0, 211, 3, T).rect(206, 4, 211, 21, T)
    c.rect(166, 18, 205, 19, '=')
    c.rect(156, 20, 205, 27, '^')
    c.rect(198, 20, 205, 27, '.').rect(198, 22, 205, 22, '_')
    c.rect(196, 20, 197, 27, '^')
    c.road([(202, 18), (202, 27)])
    c.rect(202, 22, 203, 22, '_')
    c.road([(160, 28), (202, 28)])         # the low road under the cliff
    # NE hills above the capital
    c.rect(206, 22, 211, 61, T).trees(166, 30, 205, 31)
    c.poly([(170, 34), (186, 31), (204, 32), (206, 40), (206, 54), (196, 57), (178, 57), (170, 52)], '^')
    c.poly([(176, 37), (186, 35), (200, 36), (202, 44), (200, 50), (190, 53), (178, 51)], T)
    # the Lethys: from the dam south-west round the temple, east under the park, south past
    # Reedmouth and out through the delta
    river = [(98, 26), (100, 34), (92, 44), (74, 50), (60, 58), (55, 70), (55, 82), (61, 92), (70, 99), (84, 102),
             (112, 102), (122, 106), (127, 118), (125, 130), (117, 139), (96, 144), (78, 152), (70, 166),
             (104, 166), (104, 158), (114, 150), (128, 144), (140, 136), (146, 124), (149, 112), (146, 100),
             (138, 93), (126, 92), (76, 92), (70, 88), (68, 80), (68, 66), (72, 60), (84, 56), (100, 52),
             (120, 44), (140, 36), (150, 30), (157, 26)]
    c.poly(river, '~')
    # the sea, the beach and the sandbanks of the delta
    c.poly([(58, 160), (100, 158), (140, 156), (180, 153), (212, 150), (212, 166), (58, 166)], '≈')
    c.poly([(104, 152), (140, 142), (170, 141), (212, 138), (212, 150), (180, 153), (140, 156), (104, 158)], 'b', only='.,')
    c.poly([(80, 159), (84, 158), (89, 158), (91, 159.5), (88, 161), (82, 161)], 'b')
    c.poly([(110, 161), (114, 160), (118, 161), (115, 162.5), (111, 162.5)], 'b')
    c.tidy('~≈', '~≈W')
    c.tidy('^', '^CSW_')


# ---------------------------------------------------------------- Stillbrook
def stillbrook(c):
    """Beryl's home town, after the drawing: Fighting Gym, Poké Center and Super Market in a row
    under the ridge, Jasper's home and one more house east of the road south, Beryl's home west."""
    t = Place(c, 'Stillbrook', 0, 24, 58, 72, STILLBROOK, mapsec='MAPSEC_PALLET_TOWN', music='MUS_RG_PALLET',
              weather='WEATHER_LEAVES')
    c.trees(0, 38, 1, 95)
    # main street under the top row, the path from the cave
    c.road([(2, 46), (52, 46)])
    c.road([(37, 37), (37, 45)])
    for x in (7, 20, 33):
        c.road([(x, 44), (x, 45)])
    # the road south to Route 1, and the lanes to the houses
    c.road([(27, 48), (27, 95)])
    c.road([(6, 48), (6, 63), (26, 63)])
    c.road([(29, 57), (33, 57)]).road([(29, 71), (33, 71)])
    # gardens, trees and the riverbank
    c.rect(2, 50, 4, 61, '*').rect(9, 66, 17, 68, '*').rect(35, 61, 40, 63, '*')
    c.trees(2, 66, 7, 79).trees(12, 72, 25, 87).trees(38, 76, 51, 95).trees(2, 82, 11, 95)
    c.trees(42, 38, 47, 45).trees(44, 50, 53, 57)
    c.rect(14, 89, 25, 95, ',').rect(30, 80, 37, 93, ',')
    c.rect(41, 60, 49, 70, '.').rect(43, 63, 47, 67, '~')

    gym = t.building('gym', 4, 39, 'Stillbrook_Gym')
    pokecenter(t, 18, 39, 'HEAL_LOCATION_STILLBROOK', PROJ.heal)
    mart(t, 31, 40, ['ITEM_POKE_BALL', 'ITEM_POTION', 'ITEM_ANTIDOTE', 'ITEM_PARALYZE_HEAL', 'ITEM_AWAKENING', 'ITEM_ESCAPE_ROPE'])
    home = t.building('home', 12, 58, 'Stillbrook_BerylsHouse_1F')
    jasper = t.building('home', 32, 52, 'Stillbrook_JaspersHouse')
    c.building('mailbox', 11, 61)
    c.building('mailbox', 31, 55)
    c.building('mailbox', 31, 69)
    picket(c, 8, 17, 65)
    picket(c, 34, 41, 64)
    for x, y in ((18, 61), (19, 61), (38, 56), (38, 70), (24, 50), (25, 50)):
        bush(c, x, y)

    gym_sign(t, 12, 44, 'STILLBROOK POKéMON GYM\nLEADER: TORVALD\n\nThe gym is closed while the leader is away.')
    t.sign(29, 49, 'STILLBROOK\nWhere the river slows down.')
    t.sign(10, 62, "BERYL'S HOUSE")
    t.sign(30, 56, "JASPER'S HOUSE")
    t.sign(39, 38, 'CRAGWAY CAVE')
    t.sign(54, 48, 'ROUTE 2\nUp to the LETHYS DAM')

    t.npc('OBJ_EVENT_GFX_OLD_MAN_1', 9, 47, "TORVALD's gym has been shut for years. He went off to train in the mountains.")
    t.npc('OBJ_EVENT_GFX_FAT_MAN_FRLG', 40, 47, 'The power line along the river feeds the whole town. When the dam hums, our lights stay on.', move=WANDER, rx=3, ry=1)
    t.npc('OBJ_EVENT_GFX_LITTLE_GIRL_FRLG', 20, 54, "Tag! You're it! ...Hey, wait up!", move=WANDER, rx=3, ry=2)
    t.npc('OBJ_EVENT_GFX_LITTLE_BOY_FRLG', 16, 52, "I'm the fastest kid in STILLBROOK! Nobody can catch me!", move=WANDER, rx=3, ry=2)
    t.npc('OBJ_EVENT_GFX_WOMAN_1_FRLG', 5, 52, 'I water these flowers every morning. The river water makes them grow so tall!', move='MOVEMENT_TYPE_FACE_LEFT')
    t.npc('OBJ_EVENT_GFX_FISHER', 53, 72, 'I fish in the LETHYS every morning. Grandpa says the river remembers every POKéMON that ever swam in it.', move='MOVEMENT_TYPE_FACE_RIGHT')
    t.npc('OBJ_EVENT_GFX_YOUNGSTER_FRLG', 36, 40, "One day I'll go through CRAGWAY CAVE all by myself. Mum says not yet.", move='MOVEMENT_TYPE_FACE_UP')
    t.npc('OBJ_EVENT_GFX_OLD_WOMAN_FRLG', 44, 69, 'The pond is older than the town. On quiet nights you can hear it sing.', move='MOVEMENT_TYPE_WANDER_LEFT_AND_RIGHT', rx=2)
    t.npc('OBJ_EVENT_GFX_MEOWTH', 22, 58, 'Meow?', move=WANDER, rx=2, ry=1)
    t.npc('OBJ_EVENT_GFX_PIDGEY', 9, 70, 'Pi-pidgey!', move=WANDER, rx=1, ry=1)
    t.npc('OBJ_EVENT_GFX_PSYDUCK', 48, 63, 'Psy...?', move=WANDER, rx=1, ry=0)

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
    room(t, 'home', 32, 66, 'Stillbrook_House1', 'PalletTown_RivalsHouse_Frlg',
         [('OBJ_EVENT_GFX_MAN', 4, 4, 'Before the dam was built, the LETHYS flooded STILLBROOK every spring. Now it just sits there, quiet.', WANDER),
          ('OBJ_EVENT_GFX_LITTLE_GIRL_FRLG', 9, 4, "When I grow up I'm going to be a GYM LEADER like TORVALD!")])
    return t


# ---------------------------------------------------------------- Route 1
def route1(c):
    """South of Stillbrook: the Pension with its garden and flower fields, the farm, the fields and
    the windmill. The road east goes on to Reedmouth."""
    t = Place(c, 'KaldriaRoute1', 0, 96, 58, 70, STILLBROOK, mapsec='MAPSEC_ROUTE_1', music='MUS_RG_ROUTE1',
              map_type='MAP_TYPE_ROUTE', weather='WEATHER_LEAVES')
    c.trees(0, 96, 5, 165).trees(0, 160, 57, 165)
    # the road: down from Stillbrook, east past the Pension, then south to the fields
    c.road([(27, 96), (27, 98), (41, 98), (41, 152)])
    c.road([(41, 117), (57, 117)])            # east to Reedmouth
    c.road([(13, 134), (41, 134)])            # west to the farm
    c.road([(13, 134), (13, 139)])
    # the Pension garden: flowers behind a fence, open towards the Pension
    c.rect(8, 101, 24, 121, '.').rect(10, 103, 14, 108, '*').rect(18, 110, 22, 116, '*').rect(10, 113, 14, 119, '*')
    c.fence(7, 100, 25, 122, gaps=[(25, 104), (25, 105)])
    c.trees(6, 124, 11, 131).trees(16, 124, 25, 131)
    # flower fields south of the Pension, with a shed
    c.rect(28, 106, 39, 119, '*').rect(32, 106, 33, 119, '.').rect(28, 120, 39, 128, '*')
    c.road([(32, 106), (32, 119)])
    # the farm
    c.rect(5, 140, 23, 158, '.')
    for y in (148, 150, 152, 154, 156):
        c.rect(6, y, 22, y, ':')
    c.fence(4, 139, 24, 159, gaps=[(13, 139), (14, 139)])
    # fields and arable land round the windmill
    for y in range(138, 158, 2):
        c.rect(27, y, 38, y, ':')
    for y in range(140, 158, 2):
        c.rect(48, y, 56, y, ':')
    c.road([(41, 152), (46, 152)])
    c.road([(52, 119), (52, 138)])
    c.rect(44, 100, 57, 113, ',').rect(26, 136, 39, 137, ',')
    c.trees(44, 120, 51, 133).trees(54, 120, 57, 137)

    pension = t.building('lab', 30, 100, 'KaldriaRoute1_Pension')
    c.road([(33, 105), (33, 105)])
    t.sign(36, 105, 'LETHYS PENSION\nWe look after your POKéMON!')
    t.sign(29, 100, 'ROUTE 1\nNorth: STILLBROOK\nEast: REEDMOUTH')
    t.sign(15, 137, 'BRAMBLE FARM')
    t.sign(43, 151, 'The old windmill')
    t.npc('OBJ_EVENT_GFX_MAN', 14, 152, 'The soil here is good because the river used to flood it. Since the dam, I have to water everything myself.', move=WANDER, rx=2, ry=1)
    t.npc('OBJ_EVENT_GFX_PICNICKER_FRLG', 30, 112, 'The flower fields smell lovely in the morning. The POKéMON in the tall grass think so too!', move=WANDER, rx=1, ry=2)
    t.npc('OBJ_EVENT_GFX_NIDORAN_F', 12, 111, 'Nido!', move=WANDER, rx=2, ry=2)
    t.npc('OBJ_EVENT_GFX_JIGGLYPUFF', 20, 105, 'Jiggly...', move=WANDER, rx=2, ry=2)
    t.npc('OBJ_EVENT_GFX_DODUO', 10, 144, 'Doduo! Doduo!', move=WANDER, rx=3, ry=1)
    p = Interior('KaldriaRoute1_Pension', 'FourIsland_PokemonDayCare_Frlg', {'*': ('KaldriaRoute1', pension)})
    p.npc('OBJ_EVENT_GFX_WOMAN_2_FRLG', 2, 2, "ROSALIND: Welcome to the LETHYS PENSION!\n\nMy son JASPER says he'll be a famous TRAINER one day. Until then, I look after everyone else's POKéMON.")
    t.interiors.append(p)
    room(t, 'home', 15, 141, 'KaldriaRoute1_FarmHouse', 'PalletTown_RivalsHouse_Frlg',
         [('OBJ_EVENT_GFX_WOMAN_3_FRLG', 6, 5, 'Our family has farmed by the LETHYS for five generations. Grandpa says the river used to talk to him.')])
    room(t, 'home', 33, 121, 'KaldriaRoute1_FlowerShed', 'PalletTown_RivalsHouse_Frlg',
         [('OBJ_EVENT_GFX_OLD_MAN_1', 6, 5, 'Flowers grow best where the water used to reach. Funny how the land remembers.')])
    room(t, 'home', 43, 146, 'KaldriaRoute1_Windmill', 'PalletTown_RivalsHouse_Frlg',
         [('OBJ_EVENT_GFX_HIKER_FRLG', 6, 5, "The windmill hasn't turned in years. The dam makes all the power now.")])
    return t


# ---------------------------------------------------------------- Route 2 and the dam
def route2(c):
    t = Place(c, 'KaldriaRoute2', 58, 14, 38, 44, STILLBROOK, mapsec='MAPSEC_ROUTE_2', music='MUS_RG_ROUTE1',
              map_type='MAP_TYPE_ROUTE')
    t.sign(64, 39, 'ROUTE 2\nUp: LETHYS DAM\nWest: STILLBROOK')
    t.npc('OBJ_EVENT_GFX_HIKER_FRLG', 70, 33, 'From up here you can hear the dam humming. All that water, held back by one wall!', move='MOVEMENT_TYPE_FACE_RIGHT')
    t.npc('OBJ_EVENT_GFX_YOUNGSTER_FRLG', 80, 25, 'These steps were cut when they built the dam. My legs hate them.', move=WANDER, rx=2, ry=1)
    return t


def dam(c):
    t = Place(c, 'LethysDam', 96, 0, 64, 32, STILLBROOK, mapsec='MAPSEC_ROUTE_3', music='MUS_RG_ROUTE24',
              map_type='MAP_TYPE_ROUTE')
    t.npc('OBJ_EVENT_GFX_WORKER_M', 128, 18, 'LETHYS DAM: the power for all of KALDRIA. Please stay on the walkway.', move='MOVEMENT_TYPE_WANDER_LEFT_AND_RIGHT', rx=4)
    t.npc('OBJ_EVENT_GFX_FISHER', 110, 18, 'MIRRORMERE is so still you can see the mountains in it. Not many fish bite, though.', move='MOVEMENT_TYPE_FACE_UP')
    return t


def route4(c):
    """The power station on the high ground east of the dam, the one-way drop under it, and the road
    down to the capital."""
    t = Place(c, 'KaldriaRoute4', 160, 0, 52, 58, LAVENDER, mapsec='MAPSEC_ROUTE_5', music='MUS_RG_ROUTE24',
              map_type='MAP_TYPE_ROUTE')
    c.road([(163, 28), (163, 57)])
    c.rect(166, 6, 172, 15, ',').rect(190, 6, 203, 15, ',').trees(158, 4, 163, 15)
    c.road([(180, 13), (180, 17)])
    station = t.building('power_plant', 175, 6, 'KaldriaRoute4_PowerStation')
    t.sign(178, 17, 'LETHYS POWER STATION')
    t.sign(165, 31, 'ROUTE 4\nSouth: VALECROWN CITY')
    t.npc('OBJ_EVENT_GFX_WORKER_M', 200, 17, "Careful, it's a long drop! You can jump down, but there's no way back up here.", move='MOVEMENT_TYPE_FACE_DOWN')
    ps = Interior('KaldriaRoute4_PowerStation', 'PowerPlant_Frlg', {'*': ('KaldriaRoute4', station)}, mapsec='MAPSEC_POWER_PLANT')
    ps.warps = [w for w in ps.warps if w['y'] > 30]
    ps.npc('OBJ_EVENT_GFX_SCIENTIST', 5, 34, "Every light in VALECROWN runs on the water going through those turbines. If the dam stopped, the capital would go dark.")
    t.interiors.append(ps)
    return t


def ruins(c):
    """Below the dam: the river basin and the Lowbank Ruins on its south bank."""
    t = Place(c, 'KaldriaRoute3', 96, 32, 64, 26, LAVENDER, mapsec='MAPSEC_ROUTE_4', music='MUS_RG_ROUTE3',
              map_type='MAP_TYPE_ROUTE')
    # paved ground with broken walls
    c.poly([(104, 57), (104, 53), (122, 47), (140, 41), (152, 37), (158, 37), (158, 57)], ',', only='.')
    # the floors of old houses, a few stumps of wall
    for x0, y0, x1, y1 in ((108, 51, 115, 55), (120, 47, 127, 52), (132, 42, 139, 47), (144, 41, 153, 48), (130, 51, 139, 56)):
        c.rect(x0, y0, x1, y1, 'p')
    for x, y in ((108, 51), (114, 54), (126, 47), (132, 42), (138, 46), (144, 41), (152, 47), (130, 55), (138, 51)):
        c.rect(x & ~1, y & ~1, (x & ~1) + 1, (y & ~1) + 1, '^')
    t.sign(114, 56, 'LOWBANK RUINS\nA village that stood here before the dam.')
    t.npc('OBJ_EVENT_GFX_SCIENTIST', 134, 52, 'These walls are older than the dam, older than STILLBROOK even. Who built them?', move=WANDER, rx=2, ry=1)
    t.npc('OBJ_EVENT_GFX_FISHER', 106, 55, 'People say the old village of LOWBANK is still down there, under the lake.', move='MOVEMENT_TYPE_FACE_UP')
    return t


# ---------------------------------------------------------------- Lanterncross and the park
def lanterncross(c):
    """The Lanterncross Temple: the road from the ruins goes in through the temple's gatehouse and
    out of its front doors, then over the Lethys to Reedmouth. LEADER ODA keeps her gym in the
    lantern tower inside the temple grounds. East of it, the park."""
    t = Place(c, 'Lanterncross', 58, 58, 72, 46, LAVENDER, mapsec='MAPSEC_POKEMON_TOWER', music='MUS_RG_LAVENDER')
    c.road([(82, 58), (164, 58)])           # the road from the capital past the ruins
    c.road([(84, 59), (84, 61)])
    # temple grounds: walls of trees, the gatehouse the only way in
    c.trees(72, 60, 81, 91).trees(88, 60, 99, 73).trees(96, 74, 99, 91)
    c.rect(82, 70, 95, 91, '.')
    c.road([(84, 70), (84, 91)])
    c.road([(86, 84), (90, 84)])
    c.rect(82, 72, 83, 81, '*').rect(86, 86, 95, 89, '*')
    # the park: a ring of trees, a meadow with a few trees and a pond
    c.trees(100, 62, 147, 63).trees(100, 64, 103, 91).trees(144, 64, 147, 91).trees(104, 64, 143, 65).trees(104, 88, 143, 91)
    c.rect(104, 66, 143, 87, ',', ).rect(108, 70, 139, 83, '.')
    c.trees(110, 72, 111, 73).trees(118, 78, 119, 79).trees(128, 70, 129, 71).trees(134, 80, 135, 81)
    c.rect(122, 72, 127, 75, '~')
    c.rect(120, 60, 121, 65, '=').rect(120, 62, 121, 63, '=')
    c.rect(144, 74, 147, 75, '=')
    vbridge(c, 83, 92, 101)
    c.building('gate_back', 82, 62)
    hall = t.building('gatehouse', 82, 63, 'Lanterncross_Temple')
    t.warp(85, 68, 'MAP_LANTERNCROSS_TEMPLE', 0)
    t.warp(84, 62, 'MAP_LANTERNCROSS_TEMPLE', 1)
    t.warp(85, 62, 'MAP_LANTERNCROSS_TEMPLE', 1)
    tower = t.building('tower', 88, 77, 'Lanterncross_Tower')
    t.sign(86, 60, 'LANTERNCROSS TEMPLE\nThe road goes through the temple. Please walk quietly.')
    t.sign(92, 85, 'LANTERN TOWER\nThe lanterns are lit for those the river has taken.')
    t.sign(118, 61, 'LETHYS PARK')
    t.npc('OBJ_EVENT_GFX_CHANNELER', 87, 88, 'Every year we float lanterns down the LETHYS. The river carries our thoughts to the ones we lost.')
    t.npc('OBJ_EVENT_GFX_OLD_WOMAN_FRLG', 114, 80, 'The park is the quietest place near the capital. Even the POKéMON whisper here.', move=WANDER, rx=2, ry=1)
    t.npc('OBJ_EVENT_GFX_PIKACHU_FRLG', 126, 80, 'Pika!', move=WANDER, rx=2, ry=2)
    t.npc('OBJ_EVENT_GFX_LASS_FRLG', 106, 70, 'I come here to read. The capital is so loud!', move='MOVEMENT_TYPE_FACE_DOWN')
    # the temple hall: in at the back (north), out of the front (south)
    tp = Interior('Lanterncross_Temple', 'Route5_SouthEntrance_Frlg', {
        'MAP_SAFFRON_CITY': ('Lanterncross', hall), 'MAP_ROUTE5': ('Lanterncross', 2)}, mapsec='MAPSEC_POKEMON_TOWER')
    tp.objects = []
    tp.npc('OBJ_EVENT_GFX_CHANNELER', 1, 5, 'Welcome to the LANTERNCROSS TEMPLE. Travellers may pass through. Please walk quietly.')
    tw = Interior('Lanterncross_Tower', 'PokemonTower_1F_Frlg', {'*': ('Lanterncross', tower)})
    tw.warps = [w for w in tw.warps if w['dest_map'] == 'MAP_LANTERNCROSS']
    tw.npc('OBJ_EVENT_GFX_CHANNELER', 12, 10, "LEADER ODA trains her ghosts upstairs. She isn't receiving challengers yet.")
    t.interiors += [tp, tw]
    return t


# ---------------------------------------------------------------- Reedmouth and the delta
def reedmouth(c):
    """Where the Lethys meets the sea: Grass gym, harbour, and the underpass to the capital."""
    t = Place(c, 'Reedmouth', 58, 104, 72, 40, VERMILION, mapsec='MAPSEC_VERMILION_CITY', music='MUS_RG_VERMILLION',
              map_type='MAP_TYPE_CITY')
    c.road([(58, 117), (120, 117)])
    c.road([(84, 102), (84, 116)])
    for x in (74, 94, 103):
        c.road([(x, 113), (x, 116)])
    c.road([(67, 116), (67, 116)])
    c.poly([(58, 128), (66, 127), (74, 125.5), (84, 126.5), (96, 124.5), (104, 126), (116, 125), (130, 124), (130, 166), (58, 166)], 'b', only='.,').rect(62, 120, 75, 127, 'b', only='.,')
    c.trees(58, 104, 61, 115).trees(66, 120, 75, 125)
    c.rect(106, 120, 115, 123, '*').rect(86, 120, 93, 125, '*')
    pokecenter(t, 72, 108, 'HEAL_LOCATION_REEDMOUTH', PROJ.heal)
    mart(t, 92, 109, ['ITEM_POKE_BALL', 'ITEM_GREAT_BALL', 'ITEM_POTION', 'ITEM_SUPER_POTION', 'ITEM_ANTIDOTE', 'ITEM_PARALYZE_HEAL', 'ITEM_REPEL'])
    gym = t.building('gym_brown', 100, 108, 'Reedmouth_Gym')
    under = t.building('gate', 116, 113, 'Reedmouth_Underpass')
    gym_sign(t, 108, 113, 'REEDMOUTH POKéMON GYM\nLEADER: SEDGE\nRooted in the delta!')
    t.sign(115, 116, 'UNDERPASS\nUnder the LETHYS to VALECROWN CITY', facing='BG_EVENT_PLAYER_FACING_ANY')
    t.sign(60, 116, 'REEDMOUTH\nThe river ends, the sea begins.')
    vbridge(c, 112, 136, 147)
    t.npc('OBJ_EVENT_GFX_SAILOR_FRLG', 102, 134, 'The harbour ferry runs up the LETHYS when the water is high enough. These days it hardly ever is.', move='MOVEMENT_TYPE_WANDER_LEFT_AND_RIGHT', rx=3)
    t.npc('OBJ_EVENT_GFX_FISHER', 113, 143, 'Fresh water meets salt water right here. You can catch all sorts!', move='MOVEMENT_TYPE_FACE_DOWN')
    t.npc('OBJ_EVENT_GFX_LASS_FRLG', 90, 119, 'SEDGE says the reeds clean the river before it reaches the sea.', move=WANDER, rx=1, ry=1)
    t.npc('OBJ_EVENT_GFX_SEEL', 70, 136, 'Seel!', move=WANDER, rx=2, ry=0)
    gy = Interior('Reedmouth_Gym', 'CeladonCity_Gym_Frlg', {'*': ('Reedmouth', gym)})
    gy.npc('OBJ_EVENT_GFX_GYM_GUY', 5, 15, "SEDGE isn't taking challengers yet. Come back later!")
    up = Interior('Reedmouth_Underpass', 'UndergroundPath_NorthEntrance_Frlg', {
        '*': ('Reedmouth', under), 'MAP_UNDERGROUND_PATH_NORTH_SOUTH_TUNNEL': ('Valecrown_Underpass', 3)})
    up.npc('OBJ_EVENT_GFX_POLICEMAN', 9, 6, 'The underpass runs right under the LETHYS. Down the stairs for VALECROWN CITY.')
    t.interiors += [gy, up]
    room(t, 'verm_house', 66, 112, 'Reedmouth_House1', 'VermilionCity_House1_Frlg',
         [('OBJ_EVENT_GFX_WOMAN_3_FRLG', 4, 4, 'My husband works on the boats. When the dam lets more water through, the whole harbour cheers.')])
    room(t, 'verm_hall', 106, 128, 'Reedmouth_Harbour', 'VermilionCity_PokemonFanClub_Frlg',
         [('OBJ_EVENT_GFX_SAILOR_FRLG', 5, 4, 'HARBOUR OFFICE. No ferries today, sorry. The river is too low.')])
    room(t, 'verm_house', 78, 122, 'Reedmouth_House2', 'VermilionCity_House2_Frlg',
         [('OBJ_EVENT_GFX_OLD_MAN_1', 4, 4, 'When I was a boy, the delta flooded every year and the fish came right up to our doors.')])
    return t


def delta(c):
    t = Place(c, 'LethysDelta', 58, 144, 154, 22, CELADON, mapsec='MAPSEC_ROUTE_6', music='MUS_RG_ROUTE11',
              map_type='MAP_TYPE_ROUTE')
    t.npc('OBJ_EVENT_GFX_FISHER', 84, 159, 'The LETHYS DELTA. Everything the river carries ends up here.', move='MOVEMENT_TYPE_FACE_DOWN')
    t.npc('OBJ_EVENT_GFX_TUBER_F_FRLG', 170, 147, 'The sea is so warm today!', move=WANDER, rx=3, ry=1)
    t.npc('OBJ_EVENT_GFX_SWIMMER_M_WATER', 190, 158, 'Beyond the beach there is nothing but sea. Kaldria is all there is!', move=WANDER, rx=3, ry=2)
    t.sign(160, 146, 'VALECROWN BEACH')
    return t


# ---------------------------------------------------------------- Valecrown City
def valecrown(c):
    """VALECROWN CITY, the capital, east of the Lethys."""
    t = Place(c, 'Valecrown', 130, 58, 82, 86, CELADON, mapsec='MAPSEC_CELADON_CITY', music='MUS_RG_CELADON',
              map_type='MAP_TYPE_CITY')
    # avenues and streets
    c.road([(163, 58), (163, 143)])
    c.road([(163, 62), (199, 62), (199, 143)])
    c.road([(163, 106), (205, 106)])
    c.road([(150, 142), (205, 142)])
    c.rect(202, 62, 211, 145, 'T')
    c.rect(150, 60, 162, 63, '.').trees(150, 60, 161, 63)
    # the west side, between the river and the west avenue
    for y in (71, 81, 97, 113, 128):
        c.road([(150, y), (162, y)])
    c.road([(148, 71), (148, 74), (144, 74)])
    pokecenter(t, 151, 76, 'HEAL_LOCATION_VALECROWN', PROJ.heal)
    gym = t.building('gym', 152, 92, 'Valecrown_Gym')
    gym_sign(t, 160, 96, 'VALECROWN POKéMON GYM\nLEADER: CASSIAN\nThe spark of the capital!')
    # the east blocks
    c.rect(166, 65, 197, 103, '.')
    c.rect(172, 89, 186, 96, 'p').rect(172, 99, 187, 102, '*')
    c.trees(166, 76, 173, 87).trees(188, 76, 197, 87).trees(194, 90, 197, 103).trees(166, 90, 169, 103)
    c.rect(166, 109, 197, 140, '.')
    c.road([(168, 114), (168, 116), (172, 116), (172, 140)])
    c.road([(172, 124), (197, 124)])
    c.rect(180, 127, 197, 139, ',')
    c.fence(179, 126, 198, 140, gaps=[(179, 132), (179, 133)])
    c.rect(174, 109, 177, 113, '*').rect(150, 133, 155, 140, '*')
    mart(t, 166, 67, ['ITEM_POKE_BALL', 'ITEM_GREAT_BALL', 'ITEM_ULTRA_BALL', 'ITEM_SUPER_POTION', 'ITEM_HYPER_POTION', 'ITEM_REVIVE', 'ITEM_FULL_HEAL', 'ITEM_SUPER_REPEL'])
    under = t.building('gate', 167, 110, 'Valecrown_Underpass')
    t.sign(165, 65, 'VALECROWN CITY\nThe crown of the valley.')
    t.sign(178, 128, 'VALECROWN ZOO\nMeet the POKéMON of KALDRIA!', facing='BG_EVENT_PLAYER_FACING_ANY')
    t.sign(166, 115, 'UNDERPASS\nTo REEDMOUTH', facing='BG_EVENT_PLAYER_FACING_ANY')
    t.sign(150, 69, 'RADIO TOWER')
    t.npc('OBJ_EVENT_GFX_GENTLEMAN_FRLG', 175, 64, 'The capital never sleeps. All those lights, all that power, straight from the LETHYS DAM.', move=WANDER, rx=2, ry=1)
    t.npc('OBJ_EVENT_GFX_LITTLE_BOY_FRLG', 177, 126, 'The zoo has a POKéMON from every corner of KALDRIA!', move=WANDER, rx=1, ry=1)
    t.npc('OBJ_EVENT_GFX_POLICEMAN', 186, 143, 'South of here is VALECROWN BEACH. Swim safely!', move='MOVEMENT_TYPE_FACE_DOWN')
    t.npc('OBJ_EVENT_GFX_CUBONE', 184, 130, 'Cubone...', move=WANDER, rx=3, ry=2)
    t.npc('OBJ_EVENT_GFX_MACHOP', 193, 135, 'Machop!', move=WANDER, rx=2, ry=2)
    t.npc('OBJ_EVENT_GFX_NIDORAN_M', 188, 137, 'Nido nido!', move=WANDER, rx=2, ry=1)
    t.npc('OBJ_EVENT_GFX_BEAUTY_FRLG', 182, 96, 'Shopping, shopping, shopping! This city has everything.', move=WANDER, rx=3, ry=1)
    t.npc('OBJ_EVENT_GFX_WORKER_M', 188, 107, 'They keep building and building. Every new tower needs more power from the dam.', move='MOVEMENT_TYPE_WANDER_LEFT_AND_RIGHT', rx=3)
    gy = Interior('Valecrown_Gym', 'ViridianCity_Gym_Frlg', {'*': ('Valecrown', gym)})
    gy.npc('OBJ_EVENT_GFX_GYM_GUY', 14, 20, "CASSIAN is busy keeping the city lights on. Come back later!")
    vu = Interior('Valecrown_Underpass', 'UndergroundPath_SouthEntrance_Frlg', {
        '*': ('Valecrown', under), 'MAP_UNDERGROUND_PATH_NORTH_SOUTH_TUNNEL': ('Reedmouth_Underpass', 3)})
    vu.npc('OBJ_EVENT_GFX_POLICEMAN', 9, 6, 'Down the stairs and under the river for REEDMOUTH.')
    t.interiors += [gy, vu]
    room(t, 'apartment', 151, 66, 'Valecrown_RadioTower', 'CeladonCity_House1_Frlg',
         [('OBJ_EVENT_GFX_WORKER_M', 4, 4, "KALDRIA FM! Today's news: water levels at the dam are lower than ever.")])
    room(t, 'dept_store', 175, 79, 'Valecrown_ShoppingCentre', 'CeladonCity_DepartmentStore_1F_Frlg',
         [('OBJ_EVENT_GFX_WORKER_F', 6, 10, 'Welcome to the VALECROWN SHOPPING CENTRE! The upper floors are still being built.')])
    room(t, 'casino', 152, 108, 'Valecrown_Casino', 'CeladonCity_GameCorner_Frlg',
         [('OBJ_EVENT_GFX_BALDING_MAN', 1, 6, 'The slots are switched off until the new power line is finished. Rotten luck!')])
    room(t, 'prize', 157, 124, 'Valecrown_FlowerShop', 'CeladonCity_House1_Frlg',
         [('OBJ_EVENT_GFX_WOMAN_1_FRLG', 4, 4, 'Our flowers come from the fields along ROUTE 1. The soil there is the best in KALDRIA.')])
    room(t, 'apartment', 167, 135, 'Valecrown_BikeShop', 'CeruleanCity_BikeShop_Frlg',
         [('OBJ_EVENT_GFX_MAN', 9, 3, 'Bikes! Fresh from the factory! ...Well, they will be, once the factory gets its power back.')])
    texts = ['I moved here from STILLBROOK for work. I miss the quiet, but not the floods.',
             "VALECROWN uses more power than every other town put together. Somebody has to pay for it.",
             'Did you see the zoo? My favourite is the POKéMON that lives in the reeds.',
             "The Flowkeepers held a march here last week. They want the river set free.",
             'From the top of the RADIO TOWER you can see the dam on a clear day.',
             'CASSIAN, our gym leader, keeps the city lights on during storms. What a guy!']
    spots = [(157, 76), (176, 66), (186, 66), (182, 110), (189, 110), (192, 66)]
    tpls = ['CeladonCity_House1_Frlg', 'CeruleanCity_House1_Frlg', 'CeruleanCity_House2_Frlg',
            'CeruleanCity_House3_Frlg', 'SaffronCity_House_Frlg', 'FuchsiaCity_House1_Frlg']
    gfx = ['OBJ_EVENT_GFX_WOMAN_2_FRLG', 'OBJ_EVENT_GFX_MAN', 'OBJ_EVENT_GFX_LASS_FRLG', 'OBJ_EVENT_GFX_ROCKER',
           'OBJ_EVENT_GFX_OLD_MAN_1', 'OBJ_EVENT_GFX_COOLTRAINER_M']
    for i, ((x, y), text) in enumerate(zip(spots, texts)):
        room(t, 'apartment', x, y, f'Valecrown_House{i + 1}', tpls[i], [(gfx[i], 4, 4, text, WANDER)])
        c.road([(x + 1, y + 5), (x + 1, y + 5)])
    return t


def beach(c):
    t = Place(c, 'ValecrownBeach', 130, 146, 82, 20, CELADON, mapsec='MAPSEC_ROUTE_7', music='MUS_RG_ROUTE11',
              map_type='MAP_TYPE_ROUTE')
    t.npc('OBJ_EVENT_GFX_TUBER_F_FRLG', 170, 147, 'The sea is so warm today!', move=WANDER, rx=3, ry=1)
    t.npc('OBJ_EVENT_GFX_SWIMMER_M_WATER', 190, 158, 'Beyond the beach there is nothing but sea. Kaldria is all there is!', move=WANDER, rx=3, ry=2)
    return t


def build():
    c = Canvas(W, H)
    terrain(c)
    towns = [stillbrook(c), route1(c), route2(c), dam(c), route4(c), ruins(c), lanterncross(c), reedmouth(c),
             delta(c), valecrown(c)]
    # anything no map covers is forest
    for y in range(H):
        for x in range(W):
            if not any(r.has(x, y) for r in c.regions.values()):
                c.g[y][x] = 'T'
    c.build()
    return c, towns


def main():
    c, towns = build()
    for p in c.check_edges():
        print('edge:', p)
    PROJ.mapsec_names.update(MAPSEC_NAMES)
    for t in towns:
        t.add_to(PROJ)
    PROJ.write()
    if '--render' in sys.argv:
        out = sys.argv[sys.argv.index('--render') + 1]
        os.makedirs(out, exist_ok=True)
        lays = render.layouts()
        from PIL import Image, ImageDraw
        world = Image.new('RGB', (W * 16, H * 16), (30, 30, 40))
        d = ImageDraw.Draw(world)
        for t in towns:
            im = render.render(lays[t.layout_id], grid='--grid' in sys.argv)
            im.save(os.path.join(out, t.name + '.png'))
            r = t.region
            world.paste(im, (r.x * 16, r.y * 16))
            d.rectangle([r.x * 16, r.y * 16, (r.x + r.w) * 16 - 1, (r.y + r.h) * 16 - 1], outline=(255, 255, 0))
            d.text((r.x * 16 + 4, r.y * 16 + 4), t.name, fill=(255, 255, 0))
        world.save(os.path.join(out, 'world.png'))


if __name__ == '__main__':
    main()

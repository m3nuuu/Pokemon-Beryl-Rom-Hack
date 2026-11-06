"""Kaldria: every generated map. Run `python3 tools/beryl/world.py` to (re)write them,
`python3 tools/beryl/world.py --render DIR` to also save a PNG of each outdoor map."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kaldria import Grid, Town, Interior, pokecenter, mart, Project, upper_id  # noqa: E402
import render  # noqa: E402

PROJ = Project()
# Hoenn place-name slots reused for Kaldria places
MAPSEC_NAMES = {
    'MAPSEC_LITTLEROOT_TOWN': 'STILLBROOK',
    'MAPSEC_ROUTE_101': 'ROUTE 1',
    'MAPSEC_ROUTE_102': 'ROUTE 2',
    'MAPSEC_ROUTE_103': 'LETHYS DAM',
    'MAPSEC_ROUTE_104': 'ROUTE 3',
    'MAPSEC_ROUTE_105': 'ROUTE 4',
    'MAPSEC_ROUTE_106': 'LANTERNCROSS',
    'MAPSEC_SLATEPORT_CITY': 'REEDMOUTH',
    'MAPSEC_MAUVILLE_CITY': 'VALECROWN CITY',
    'MAPSEC_ROUTE_107': 'LETHYS DELTA',
    'MAPSEC_ROUTE_108': 'VALECROWN BEACH',
}
TOWNS = []


def stillbrook():
    """Beryl's home town, south-west Kaldria. North: the ridge and Cragway Cave.
    East: Route 2 climbs to the Lethys Dam. South: Route 1 to the Pension and Reedmouth."""
    W, H = 48, 44
    g = Grid(W, H)
    # the ridge along the north edge, with the cave mouth
    g.rect(0, 0, W - 1, 4, '^').rect(0, 5, 13, 5, '^').rect(38, 5, W - 1, 6, '^')
    g.put(30, 4, 'C')
    g.rect(29, 5, 31, 6, '.')
    # west forest edge and south-west woods
    g.trees(0, 6, 1, H - 1)
    g.trees(0, 36, 13, H - 1)
    # main street
    g.rect(2, 12, W - 1, 13, '=')
    # path from the cave down to the street
    g.rect(30, 5, 31, 11, '=')
    # the road south to Route 1
    g.rect(20, 14, 21, H - 1, '=')
    # paths to the houses
    g.rect(9, 23, 21, 24, '=')       # home
    g.rect(22, 23, 27, 23, '=')      # Jasper's house
    g.rect(22, 31, 28, 31, '=')      # house
    # gardens and flowers
    g.rect(4, 25, 12, 25, '*').rect(4, 17, 5, 22, '*')
    g.rect(24, 17, 25, 20, '*').rect(31, 21, 33, 21, '*')
    g.rect(14, 7, 14, 10, '*').rect(21, 7, 22, 10, '*')
    # the Lethys runs past the south-east corner
    for y in range(28, H):
        x0 = max(36, 46 - (y - 28))
        g.rect(x0, y, W - 1, y, '≈')
    g.trees(34, 14, 47, 27)
    g.trees(24, 34, 35, H - 1)
    g.trees(14, 38, 19, H - 1)
    g.trees(22, 38, 23, H - 1)
    # trees between the buildings on the top row
    g.trees(10, 6, 13, 11)
    g.trees(38, 7, 47, 11)

    t = Town('Stillbrook', g)
    gym = t.building('gym', 3, 7, 'Stillbrook_Gym')
    pokecenter(t, 16, 8, 'HEAL_LOCATION_STILLBROOK', PROJ.heal)
    mart(t, 33, 8, ['ITEM_POKE_BALL', 'ITEM_POTION', 'ITEM_ANTIDOTE', 'ITEM_PARALYZE_HEAL', 'ITEM_AWAKENING'])
    home = t.building('home', 6, 19, 'Stillbrook_BerylsHouse_1F')
    jasper = t.building('home_b', 26, 18, 'Stillbrook_JaspersHouse_1F')
    house = t.building('house4', 27, 27, 'Stillbrook_House1')

    t.sign(9, 11, 'STILLBROOK GYM\nLEADER: TORVALD\n\nThe gym is closed while the leader is away.', facing='BG_EVENT_PLAYER_FACING_ANY')
    t.sign(19, 14, 'STILLBROOK\nWhere the river slows down.')
    t.sign(12, 22, "BERYL'S HOUSE")
    t.sign(25, 22, "JASPER'S HOUSE")
    t.sign(32, 6, 'CRAGWAY CAVE\nAhead: CRAGMOOR')
    t.npc('OBJ_EVENT_GFX_FAT_MAN', 25, 14, 'The power line along the river feeds the whole town. When the dam hums, our lights stay on.', move='MOVEMENT_TYPE_WANDER_AROUND', rx=2, ry=1)
    t.npc('OBJ_EVENT_GFX_GIRL_1', 13, 27, 'I fish in the LETHYS every morning. Grandpa says it remembers every POKéMON that ever swam in it.', move='MOVEMENT_TYPE_WANDER_AROUND', rx=1, ry=1)
    t.npc('OBJ_EVENT_GFX_OLD_MAN', 4, 13, "TORVALD's gym has been shut for years. He went off to train in the mountains.", move='MOVEMENT_TYPE_FACE_DOWN')

    # ---- insides
    links_home = {'MAP_LITTLEROOT_TOWN': ('Stillbrook', home), 'MAP_LITTLEROOT_TOWN_BRENDANS_HOUSE_2F': ('Stillbrook_BerylsHouse_2F', None)}
    h1 = Interior('Stillbrook_BerylsHouse_1F', 'LittlerootTown_BrendansHouse_1F', links_home)
    h1.npc('OBJ_EVENT_GFX_WOMAN_4', 2, 6, "GRANDMA: Good morning, dear! Did you sleep well?\n\nDon't go too far without a POKéMON. The tall grass is full of them.", local='LOCALID_BERYLS_GRANDMA')
    h2 = Interior('Stillbrook_BerylsHouse_2F', 'LittlerootTown_BrendansHouse_2F',
                  {'MAP_LITTLEROOT_TOWN_BRENDANS_HOUSE_1F': ('Stillbrook_BerylsHouse_1F', None)}, keep_bgs=True)
    links_j = {'MAP_LITTLEROOT_TOWN': ('Stillbrook', jasper), 'MAP_LITTLEROOT_TOWN_MAYS_HOUSE_2F': ('Stillbrook_JaspersHouse_2F', None)}
    j1 = Interior('Stillbrook_JaspersHouse_1F', 'LittlerootTown_MaysHouse_1F', links_j)
    j1.npc('OBJ_EVENT_GFX_WOMAN_2', 8, 6, "ROSALIND: Oh, hello, BERYL! JASPER is upstairs, as always.\n\nI'm off to the PENSION soon. Somebody has to look after all those POKéMON!")
    j2 = Interior('Stillbrook_JaspersHouse_2F', 'LittlerootTown_MaysHouse_2F',
                  {'MAP_LITTLEROOT_TOWN_MAYS_HOUSE_1F': ('Stillbrook_JaspersHouse_1F', None)}, keep_bgs=True)
    j2.npc('OBJ_EVENT_GFX_RIVAL_BRENDAN_NORMAL', 4, 2, "JASPER: Hey, BERYL! One day I'll have a POKéMON and we'll battle every day!", move='MOVEMENT_TYPE_FACE_DOWN')
    hs = Interior('Stillbrook_House1', 'PetalburgCity_House1', {'MAP_PETALBURG_CITY': ('Stillbrook', house)})
    hs.npc('OBJ_EVENT_GFX_EXPERT_M', 4, 4, 'Before the dam was built, the LETHYS flooded STILLBROOK every spring. Now it just sits there, quiet.')
    gy = Interior('Stillbrook_Gym', 'DewfordTown_Gym', {'MAP_DEWFORD_TOWN': ('Stillbrook', gym)})
    gy.npc('OBJ_EVENT_GFX_MAN_2', 5, 24, 'The leader, TORVALD, is away. Come back when he returns!')
    t.interiors += [h1, h2, j1, j2, hs, gy]
    return t


def route1():
    """South of Stillbrook: the Pension and its garden, flower fields, the farm and the windmill.
    The road east goes on to Reedmouth."""
    W, H = 48, 74
    g = Grid(W, H)
    g.trees(0, 0, 1, H - 1).trees(0, H - 2, W - 1, H - 1)
    # the Lethys passes the north-east corner
    for y in range(0, 6):
        g.rect(36 + 2 * y, y, W - 1, y, '≈')
    g.trees(40, 6, W - 1, 33).trees(36, 8, 39, 25)
    g.trees(W - 4, 36, W - 1, H - 1)
    # roads
    g.rect(20, 0, 21, 35, '=')               # from Stillbrook
    g.rect(10, 34, W - 1, 35, '=')           # east to Reedmouth
    g.rect(10, 36, 11, 51, '=')              # south to the farm
    g.rect(40, 36, 41, 52, '=')              # to the windmill
    # Pension garden, fenced, with flowers and a gate by the road
    g.rect(5, 13, 16, 29, '.')
    g.rect(6, 15, 9, 18, '*').rect(12, 22, 15, 25, '*').rect(6, 25, 8, 27, '*')
    g.fence(4, 12, 17, 30, gaps=[(17, 20), (17, 21)])
    g.rect(18, 20, 19, 21, '=')
    g.trees(2, 2, 15, 9)
    # flower fields
    g.rect(4, 38, 8, 41, '*').rect(13, 37, 17, 42, '*').rect(24, 44, 31, 47, '*')
    # tall grass fields
    g.rect(22, 54, 37, 69, ',').rect(2, 40, 3, 49, ',').rect(42, 56, 43, 69, ',')
    g.trees(24, 22, 35, 31)
    # farm: fence, field rows, farmhouse
    g.fence(3, 52, 19, 70, gaps=[(10, 52), (11, 52)])
    from mapgen import blk
    for y in (61, 63, 65, 67):
        for x in range(5, 18):
            g.over[(x, y)] = blk(0x14C, 0, 3)  # tilled soil
    g.trees(14, 38, 17, 41)

    t = Town('KaldriaRoute1', g, mapsec='MAPSEC_ROUTE_101', music='MUS_ROUTE101', map_type='MAP_TYPE_ROUTE')
    pension = t.building('lab', 22, 14, 'KaldriaRoute1_Pension')
    farm = t.building('house5', 8, 55, 'KaldriaRoute1_FarmHouse')
    shed = t.building('cottage', 26, 38, 'KaldriaRoute1_House')
    mill = t.building('house4', 38, 53, 'KaldriaRoute1_Windmill')
    t.sign(19, 13, 'LETHYS PENSION\nWe look after your POKéMON!')
    t.sign(19, 1, 'ROUTE 1\nNorth: STILLBROOK\nEast: REEDMOUTH')
    t.sign(12, 51, 'BRAMBLE FARM')
    t.sign(42, 52, 'The old windmill')
    t.npc('OBJ_EVENT_GFX_MAN_1', 14, 58, 'The soil here is good because the river used to flood it. Since the dam, I have to water everything myself.', move='MOVEMENT_TYPE_WANDER_AROUND', rx=2, ry=1)
    t.npc('OBJ_EVENT_GFX_GIRL_3', 30, 35, 'The flower fields smell lovely in the morning. The POKéMON in the tall grass think so too!', move='MOVEMENT_TYPE_WANDER_AROUND', rx=2, ry=0)
    t.npc('OBJ_EVENT_GFX_ZIGZAGOON_1', 8, 20, 'Zigzag!', move='MOVEMENT_TYPE_WANDER_AROUND', rx=2, ry=2)
    t.npc('OBJ_EVENT_GFX_POOCHYENA', 13, 16, 'Grrr... woof!', move='MOVEMENT_TYPE_WANDER_AROUND', rx=2, ry=2)
    t.npc('OBJ_EVENT_GFX_AZUMARILL', 10, 27, 'Rill!', move='MOVEMENT_TYPE_WANDER_AROUND', rx=2, ry=1)

    p = Interior('KaldriaRoute1_Pension', 'Route117_PokemonDayCare', {'MAP_ROUTE117': ('KaldriaRoute1', pension)})
    p.npc('OBJ_EVENT_GFX_WOMAN_2', 2, 2, "ROSALIND: Welcome to the LETHYS PENSION!\n\nMy son JASPER says he'll be a famous TRAINER one day. Until then, I look after everyone else's POKéMON.")
    f = Interior('KaldriaRoute1_FarmHouse', 'PetalburgCity_House1', {'MAP_PETALBURG_CITY': ('KaldriaRoute1', farm)})
    f.npc('OBJ_EVENT_GFX_WOMAN_5', 4, 4, 'Our family has farmed by the LETHYS for five generations. Grandpa says the river used to talk to him.')
    h = Interior('KaldriaRoute1_House', 'PetalburgCity_House1', {'MAP_PETALBURG_CITY': ('KaldriaRoute1', shed)})
    h.npc('OBJ_EVENT_GFX_OLD_MAN', 4, 4, 'Flowers grow best where the water used to reach. Funny how the land remembers.')
    m = Interior('KaldriaRoute1_Windmill', 'PetalburgCity_House1', {'MAP_PETALBURG_CITY': ('KaldriaRoute1', mill)})
    m.npc('OBJ_EVENT_GFX_HIKER', 4, 4, "The windmill hasn't turned in years. The dam makes all the power now.")
    t.interiors += [p, f, h, m]
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
    t = Town('KaldriaRoute2', g, mapsec='MAPSEC_ROUTE_102', music='MUS_ROUTE101', map_type='MAP_TYPE_ROUTE')
    t.sign(12, 27, 'ROUTE 2\nUp: LETHYS DAM\nWest: STILLBROOK')
    t.npc('OBJ_EVENT_GFX_HIKER', 16, 18, 'From up here you can hear the dam humming. All that water, held back by one wall!', move='MOVEMENT_TYPE_FACE_RIGHT')
    return t


def dam():
    """The Lethys Dam: Mirrormere above, the crest road across, the spillway falling to the river below."""
    from mapgen import blk
    W, H = 56, 20
    g = Grid(W, H)
    g.rect(0, 0, W - 1, 6, '≈')
    g.rect(0, 7, W - 1, 13, '#')               # the wall, drawn below
    g.rect(24, 11, 31, 13, 'W')                # spillway
    for y in range(14, H):
        a = 22 - (y - 14) // 2
        g.rect(a, y, 55 - a - 2, y, '≈')
    g.trees(0, 14, 15, H - 1).trees(40, 14, W - 1, H - 1)
    rows = [(0x2F2, 1, 0), (0x2FA, 0, 3), (0x302, 0, 3), (0x30A, 1, 0), (0x312, 1, 0), (0x312, 1, 0), (0x312, 1, 0)]
    pillar = [(0x2F2, 1, 0), (0x2FA, 0, 3), (0x302, 0, 3), (0x30A, 1, 0), (0x30D, 1, 0), (0x315, 1, 0), (0x31D, 1, 0)]
    for x in range(W):
        col = pillar if x % 7 == 3 else rows
        for j, (m, c, e) in enumerate(col):
            if g.g[7 + j][x] == 'W':
                continue
            g.over[(x, 7 + j)] = blk(m, c, e)
    t = Town('LethysDam', g, secondary='gTileset_Mauville', mapsec='MAPSEC_ROUTE_103', music='MUS_ROUTE110', map_type='MAP_TYPE_ROUTE')
    t.npc('OBJ_EVENT_GFX_WORKER_M', 30, 8, 'LETHYS DAM: the power for all of KALDRIA. Please stay on the walkway.', move='MOVEMENT_TYPE_WANDER_LEFT_AND_RIGHT', rx=4)
    return t


def route3():
    """Below the dam: the Lethys runs south-west past Stillbrook; the Lowbank Ruins; the road
    from the power station side to the Lanterncross Temple and the capital."""
    W, H = 84, 36
    g = Grid(W, H)
    # the river from the spillway down to the south-west corner
    for y in range(H):
        cx = max(8, 56 - y * 3.4)
        g.rect(0 if y >= 14 else int(cx - 8), y, int(cx + 7), y, '≈')
    g.trees(0, 0, 25, 11)
    g.trees(66, 0, W - 1, 3).trees(74, 4, W - 1, 21)
    # Lowbank Ruins: broken walls on stone paving
    g.rect(52, 6, 70, 17, 'p')
    for x0, y0, x1, y1 in ((52, 6, 55, 8), (60, 6, 63, 7), (67, 9, 70, 11), (52, 14, 53, 17), (64, 14, 66, 15)):
        g.rect(x0, y0, x1, y1, '^')
    g.rect(58, 9, 62, 12, '^').put(60, 12, 'C')
    # roads
    g.rect(22, 26, W - 1, 27, '=')
    g.rect(22, 28, 23, H - 1, '=')             # into the temple
    g.rect(62, 18, 63, 25, '=')                # up to the ruins
    g.rect(70, 28, 71, H - 1, '=')             # down into the capital
    g.rect(30, 20, 44, 24, ',').rect(46, 29, 60, 33, ',')
    g.trees(26, 30, 43, H - 1).trees(74, 28, W - 1, H - 1).trees(30, 12, 47, 17)
    t = Town('KaldriaRoute3', g, mapsec='MAPSEC_ROUTE_104', music='MUS_ROUTE101', map_type='MAP_TYPE_ROUTE')
    t.sign(64, 18, 'LOWBANK RUINS\nA village that stood here before the dam.')
    t.sign(24, 28, 'South: LANTERNCROSS TEMPLE')
    t.sign(72, 28, 'South: VALECROWN CITY')
    t.npc('OBJ_EVENT_GFX_FISHERMAN', 40, 25, 'People say the old village of LOWBANK is still down there, under the lake. These ruins are all that was left above water.', move='MOVEMENT_TYPE_FACE_LEFT')
    t.npc('OBJ_EVENT_GFX_SCIENTIST_1', 57, 14, 'These walls are older than the dam, older than STILLBROOK even. Who built them?', move='MOVEMENT_TYPE_WANDER_AROUND', rx=2, ry=1)
    return t


def route4():
    """East of the dam: the power station on the high ground, the one-way drop below it,
    and the long road south to the capital."""
    W, H = 40, 66
    g = Grid(W, H)
    g.trees(0, 0, 9, 15).trees(W - 2, 0, W - 1, H - 1)
    g.rect(0, 0, 1, 17, '^')
    # high ground: crest road from the dam to the power station, road from Weirhaven
    g.rect(0, 18, 31, 19, '=')
    g.rect(32, 0, 33, 29, '=')
    # the cliff below the power station; the road from Weirhaven drops down a ledge
    g.rect(0, 20, W - 3, 22, '^').rect(0, 23, 3, 29, '^')
    g.rect(32, 21, 33, 21, '_')
    g.rect(32, 20, 33, 20, '=').rect(32, 22, 33, 22, '=')
    # low ground: long road south
    g.rect(14, 30, 33, 31, '=').rect(14, 32, 15, H - 1, '=')
    g.rect(0, 56, 13, 57, '=')                 # west to Route 3
    g.trees(0, 30, 11, 53).trees(18, 34, 35, 63).trees(0, 60, 11, H - 1)
    g.rect(4, 32, 11, 50, ',').rect(18, 24, 29, 28, ',')
    t = Town('KaldriaRoute4', g, secondary='gTileset_Fortree', mapsec='MAPSEC_ROUTE_105', music='MUS_ROUTE110', map_type='MAP_TYPE_ROUTE')
    station = t.building('institute', 12, 6, 'KaldriaRoute4_PowerStation')
    t.sign(31, 17, 'LETHYS POWER STATION')
    t.sign(16, 33, 'ROUTE 4\nSouth: VALECROWN CITY\nNorth: WEIRHAVEN')
    ps = Interior('KaldriaRoute4_PowerStation', 'Route119_WeatherInstitute_1F',
                  {'MAP_ROUTE119': ('KaldriaRoute4', station), 'MAP_ROUTE119_WEATHER_INSTITUTE_2F': ('KaldriaRoute4', station)})
    ps.warps = ps.warps[:2]
    ps.npc('OBJ_EVENT_GFX_SCIENTIST_1', 5, 5, "Every light in VALECROWN runs on the water going through those turbines. If the dam stopped, the capital would go dark.")
    t.interiors.append(ps)
    return t


def vbridge(g, x, y0, y1):
    """A north-south bridge (Mauville tiles), 5 wide, over water from y0 to y1."""
    from mapgen import blk
    for y in range(y0, y1 + 1):
        for i, (m, e) in enumerate(((0x328, 1), (0x2E5, 15), (0x2FE, 15), (0x2E6, 15), (0x329, 1))):
            g.over[(x + i, y)] = blk(m, 0, e)


def lanterncross():
    """The Lanterncross Temple. The road from Route 3 enters the north gate, runs through the
    temple hall and comes out of the main doors, then crosses the Lethys to Reedmouth."""
    W, H = 52, 20
    g = Grid(W, H)
    for y in range(H):
        a = 0 if y < 6 else int((y - 6) * 1.5)
        g.rect(a, y, a + 15, y, '≈')
    g.rect(16, 0, 21, 6, '.')
    # north courtyard
    g.rect(20, 0, 25, 0, '.').rect(22, 0, 23, 5, 'p').rect(18, 5, 40, 6, 'p')
    g.trees(24, 0, 25, 1).trees(36, 0, 51, 3)
    # the temple wall
    g.rect(16, 7, 51, 8, '^')
    # main temple and its plaza
    g.rect(22, 14, 40, 15, 'p').rect(30, 16, 32, 16, 'p')
    g.trees(20, 9, 23, 13).trees(38, 9, 41, 13)
    # the park east of the temple
    g.trees(44, 9, 51, 11).rect(43, 12, 51, 19, '.').rect(45, 14, 49, 17, '*').trees(46, 18, 51, 19)
    vbridge(g, 29, 16, H - 1)
    t = Town('Lanterncross', g, secondary='gTileset_Mauville', mapsec='MAPSEC_ROUTE_106', music='MUS_MT_PYRE', map_type='MAP_TYPE_TOWN')
    gate = t.building('mv_house5', 27, 1, 'Lanterncross_Temple')
    hall = t.building('mv_gamecorner', 28, 10, None)
    hall_door = t.warp(31, 13, 'MAP_LANTERNCROSS_TEMPLE', 0)
    t.warps[gate]['dest_warp_id'] = '1'
    t.sign(26, 5, 'LANTERNCROSS TEMPLE\nNorth gate')
    t.sign(33, 14, 'LANTERNCROSS TEMPLE\nThe lanterns are lit for those the river has taken.')
    t.npc('OBJ_EVENT_GFX_CHANNELER', 35, 15, 'Every year we float lanterns down the LETHYS. The river carries our thoughts to the ones we lost.', move='MOVEMENT_TYPE_FACE_DOWN')
    t.npc('OBJ_EVENT_GFX_OLD_WOMAN', 46, 13, 'The park is the quietest place near the capital. Even the POKéMON whisper here.', move='MOVEMENT_TYPE_WANDER_AROUND', rx=2, ry=1)
    tp = Interior('Lanterncross_Temple', 'MtPyre_1F', {
        ('MAP_ROUTE122', '0'): ('Lanterncross', hall_door), ('MAP_MT_PYRE_EXTERIOR', '0'): ('Lanterncross', gate),
        ('MAP_MT_PYRE_2F', '0'): ('Lanterncross_Temple2F', 0), ('MAP_MT_PYRE_2F', '4'): ('Lanterncross_Temple2F', 4)})
    tp.npc('OBJ_EVENT_GFX_CHANNELER', 12, 10, 'Welcome to the LANTERNCROSS TEMPLE. The path to the south gate runs through this hall. Please walk quietly.')
    t2 = Interior('Lanterncross_Temple2F', 'MtPyre_2F', {
        'MAP_MT_PYRE_1F': ('Lanterncross_Temple', None), 'MAP_MT_PYRE_3F': ('Lanterncross_Temple', 4)})
    t2.npc('OBJ_EVENT_GFX_CHANNELER', 6, 6, "LEADER ODA trains her ghosts up here. She isn't receiving challengers yet.")
    t.interiors += [tp, t2]
    return t


def reedmouth():
    """Where the Lethys meets the sea: Grass gym, harbour, and the underpass to the capital."""
    W, H = 52, 36
    g = Grid(W, H)
    for y in range(H):
        a = min(36, 21 + int(y * 1.5))
        g.rect(a, y, W - 1, y, '≈')
    g.rect(0, 30, 35, H - 1, '≈').rect(0, 28, 33, 29, 'b')
    vbridge(g, 29, 0, 6)
    g.trees(0, 0, 19, 3).trees(0, 10, 1, 27)
    # streets
    g.rect(0, 8, 33, 9, 'R').rect(30, 7, 33, 9, 'R').rect(18, 10, 19, 27, 'R').rect(2, 26, 33, 27, 'R')
    g.rect(31, 10, 32, 17, 'R')
    g.rect(22, 0, 28, 6, '.').trees(22, 0, 27, 3)
    t = Town('Reedmouth', g, secondary='gTileset_Mauville', mapsec='MAPSEC_SLATEPORT_CITY', music='MUS_SLATEPORT', map_type='MAP_TYPE_CITY')
    pokecenter(t, 4, 4, 'HEAL_LOCATION_REEDMOUTH', PROJ.heal)
    mart(t, 12, 4, ['ITEM_POKE_BALL', 'ITEM_GREAT_BALL', 'ITEM_POTION', 'ITEM_SUPER_POTION', 'ITEM_ANTIDOTE', 'ITEM_PARALYZE_HEAL', 'ITEM_REPEL'])
    gym = t.building('gym', 6, 14, 'Reedmouth_Gym')
    under = t.building('mv_house', 29, 18, 'Reedmouth_Underpass')
    h1 = t.building('mv_house', 22, 13, 'Reedmouth_House1')
    harbour = t.building('mv_house5', 22, 21, 'Reedmouth_Harbour')
    h2 = t.building('mv_house', 2, 20, 'Reedmouth_House2')
    t.sign(10, 19, 'REEDMOUTH GYM\nLEADER: SEDGE\nRooted in the delta!', facing='BG_EVENT_PLAYER_FACING_ANY')
    t.sign(28, 22, 'UNDERPASS\nUnder the LETHYS to VALECROWN CITY', facing='BG_EVENT_PLAYER_FACING_ANY')
    t.sign(1, 7, 'REEDMOUTH\nThe river ends, the sea begins.')
    t.npc('OBJ_EVENT_GFX_SAILOR', 12, 28, 'The harbour ferry runs up the LETHYS when the water is high enough. These days it hardly ever is.', move='MOVEMENT_TYPE_WANDER_LEFT_AND_RIGHT', rx=3)
    t.npc('OBJ_EVENT_GFX_FISHERMAN', 30, 28, 'Fresh water meets salt water right here. You can catch all sorts!', move='MOVEMENT_TYPE_FACE_DOWN')
    t.npc('OBJ_EVENT_GFX_GIRL_2', 16, 12, 'SEDGE says the reeds clean the river before it reaches the sea.', move='MOVEMENT_TYPE_WANDER_AROUND', rx=1, ry=1)
    gy = Interior('Reedmouth_Gym', 'RustboroCity_Gym', {'MAP_RUSTBORO_CITY': ('Reedmouth', gym)})
    up = Interior('Reedmouth_Underpass', 'Route110_SeasideCyclingRoadSouthEntrance', {
        ('MAP_ROUTE110', '4'): ('Reedmouth', under), ('MAP_ROUTE110', '5'): ('Valecrown', 'auto')})
    up.npc('OBJ_EVENT_GFX_POLICEMAN', 7, 2, 'The underpass runs right under the LETHYS. Left: REEDMOUTH. Right: VALECROWN CITY.')
    i1 = Interior('Reedmouth_House1', 'PetalburgCity_House1', {'MAP_PETALBURG_CITY': ('Reedmouth', h1)})
    i1.npc('OBJ_EVENT_GFX_WOMAN_3', 4, 4, 'My husband works on the boats. When the dam lets more water through, the whole harbour cheers.')
    i2 = Interior('Reedmouth_House2', 'PetalburgCity_House1', {'MAP_PETALBURG_CITY': ('Reedmouth', h2)})
    i2.npc('OBJ_EVENT_GFX_OLD_MAN', 4, 4, 'When I was a boy, the delta flooded every year and the fish came right up to our doors.')
    hb = Interior('Reedmouth_Harbour', 'PetalburgCity_House1', {'MAP_PETALBURG_CITY': ('Reedmouth', harbour)})
    hb.npc('OBJ_EVENT_GFX_SAILOR', 4, 4, 'HARBOUR OFFICE. No ferries today, sorry. The river is too low.')
    t.interiors += [gy, up, i1, i2, hb]
    return t


def valecrown():
    """VALECROWN CITY, the capital, across the river from Reedmouth."""
    W, H = 72, 60
    g = Grid(W, H)
    g.rect(0, 0, 3, H - 1, '≈').rect(0, 52, W - 1, H - 1, 'b')
    g.trees(4, 0, 15, 5).trees(22, 0, 43, 3).trees(50, 0, W - 1, 3).trees(W - 2, 4, W - 1, 51)
    # avenues
    g.rect(18, 0, 19, 51, 'R').rect(46, 0, 47, 51, 'R')
    g.rect(6, 10, 67, 11, 'R').rect(6, 26, 67, 27, 'R').rect(6, 42, 67, 43, 'R')
    g.rect(6, 12, 7, 41, 'R').rect(32, 12, 33, 49, 'R').rect(60, 12, 61, 41, 'R')
    # zoo: a fenced field with POKéMON
    g.rect(49, 29, 66, 39, ',')
    g.fence(48, 28, 67, 40, gaps=[(57, 28), (58, 28)])
    # flower shop garden, a fountain square and some greenery between the blocks
    g.rect(49, 48, 56, 49, '*').rect(54, 44, 56, 47, '*')
    g.rect(36, 36, 43, 39, '≈').rect(35, 35, 44, 35, 'p').rect(35, 40, 44, 40, 'p').rect(35, 36, 35, 39, 'p').rect(44, 36, 44, 39, 'p')
    g.trees(8, 12, 15, 19).trees(50, 12, 57, 19).trees(36, 12, 43, 15).trees(22, 30, 29, 33).trees(8, 30, 15, 35)
    g.rect(20, 46, 31, 49, '*')
    g.trees(4, 46, 15, 51).trees(52, 46, 67, 51)
    t = Town('Valecrown', g, secondary='gTileset_Mauville', mapsec='MAPSEC_MAUVILLE_CITY', music='MUS_LILYCOVE', map_type='MAP_TYPE_CITY')
    gym = t.building('gym', 22, 15, 'Valecrown_Gym')
    pokecenter(t, 10, 6, 'HEAL_LOCATION_VALECROWN', PROJ.heal)
    mart(t, 36, 6, ['ITEM_POKE_BALL', 'ITEM_GREAT_BALL', 'ITEM_ULTRA_BALL', 'ITEM_SUPER_POTION', 'ITEM_HYPER_POTION', 'ITEM_REVIVE', 'ITEM_FULL_HEAL', 'ITEM_SUPER_REPEL'])
    shop = t.building('mv_house5', 50, 6, 'Valecrown_ShoppingCentre')
    t.building('mv_tower', 56, 5, None)
    casino = t.building('mv_gamecorner', 36, 30, 'Valecrown_Casino')
    tower = t.building('mv_house', 22, 6, 'Valecrown_RadioTower')
    t.building('mv_tower', 27, 5, None)
    bikes = t.building('mv_bikeshop', 50, 21, 'Valecrown_BikeShop')
    flowers = t.building('mv_house', 50, 44, 'Valecrown_FlowerShop')
    t.building('mv_house', 8, 37, 'Reedmouth_Underpass', dest_warp=2)
    houses = [t.building('mv_house', 10, 21, 'Valecrown_House1'), t.building('mv_house5', 22, 37, 'Valecrown_House2'),
              t.building('mv_house', 62, 21, 'Valecrown_House3'), t.building('mv_house', 24, 21, 'Valecrown_House4'),
              t.building('mv_house5', 36, 21, 'Valecrown_House5'), t.building('mv_house', 62, 5, 'Valecrown_House6')]
    t.sign(28, 19, 'VALECROWN GYM\nLEADER: CASSIAN\nThe spark of the capital!', facing='BG_EVENT_PLAYER_FACING_ANY')
    t.sign(20, 12, 'VALECROWN CITY\nThe crown of the valley.')
    t.sign(28, 9, 'RADIO TOWER\nKALDRIA FM: news from the river.', facing='BG_EVENT_PLAYER_FACING_ANY')
    t.sign(56, 27, 'VALECROWN ZOO\nMeet the POKéMON of KALDRIA!', facing='BG_EVENT_PLAYER_FACING_ANY')
    t.sign(54, 9, 'VALECROWN SHOPPING CENTRE', facing='BG_EVENT_PLAYER_FACING_ANY')
    t.sign(12, 40, 'UNDERPASS\nTo REEDMOUTH', facing='BG_EVENT_PLAYER_FACING_ANY')
    t.npc('OBJ_EVENT_GFX_GENTLEMAN', 30, 12, 'The capital never sleeps. All those lights, all that power, straight from the LETHYS DAM.', move='MOVEMENT_TYPE_WANDER_AROUND', rx=2, ry=1)
    t.npc('OBJ_EVENT_GFX_TWIN', 44, 28, 'The zoo has a POKéMON from every corner of KALDRIA!', move='MOVEMENT_TYPE_WANDER_AROUND', rx=1, ry=1)
    t.npc('OBJ_EVENT_GFX_POLICEMAN', 46, 45, 'South of here is VALECROWN BEACH. Swim safely!', move='MOVEMENT_TYPE_FACE_DOWN')
    t.npc('OBJ_EVENT_GFX_ZIGZAGOON_1', 52, 33, 'Zig!', move='MOVEMENT_TYPE_WANDER_AROUND', rx=3, ry=2)
    t.npc('OBJ_EVENT_GFX_AZUMARILL', 62, 36, 'Rill rill!', move='MOVEMENT_TYPE_WANDER_AROUND', rx=2, ry=2)
    t.npc('OBJ_EVENT_GFX_POOCHYENA', 56, 31, 'Grr!', move='MOVEMENT_TYPE_WANDER_AROUND', rx=2, ry=2)
    rooms = [
        ('Valecrown_Gym', 'RustboroCity_Gym', gym, 'MAP_RUSTBORO_CITY', None),
        ('Valecrown_ShoppingCentre', 'MauvilleCity_Mart', shop, 'MAP_MAUVILLE_CITY', 'Welcome to the VALECROWN SHOPPING CENTRE! The upper floors are still being built.'),
        ('Valecrown_Casino', 'MauvilleCity_GameCorner', casino, 'MAP_MAUVILLE_CITY', None),
        ('Valecrown_RadioTower', 'PetalburgCity_House1', tower, 'MAP_PETALBURG_CITY', "KALDRIA FM! Today's news: water levels at the dam are lower than ever."),
        ('Valecrown_BikeShop', 'MauvilleCity_BikeShop', bikes, 'MAP_MAUVILLE_CITY', None),
        ('Valecrown_FlowerShop', 'PetalburgCity_House1', flowers, 'MAP_PETALBURG_CITY', 'Our flowers come from the fields along ROUTE 1. The soil there is the best in KALDRIA.'),
    ]
    texts = ['I moved here from STILLBROOK for work. I miss the quiet, but not the floods.',
             "VALECROWN uses more power than every other town put together. Somebody has to pay for it.",
             'Did you see the zoo? My favourite is the POKéMON that lives in the reeds.',
             "The Flowkeepers held a march here last week. They want the river set free.",
             'From the top of the RADIO TOWER you can see the dam on a clear day.',
             'CASSIAN, our gym leader, keeps the city lights on during storms. What a guy!']
    for i, d in enumerate(houses):
        rooms.append((f'Valecrown_House{i + 1}', 'PetalburgCity_House1', d, 'MAP_PETALBURG_CITY', texts[i]))
    for name, tpl, door, tdest, text in rooms:
        it = Interior(name, tpl, {tdest: ('Valecrown', door)}, music=None)
        it.warps = [w for w in it.warps if w['dest_map'] == 'MAP_VALECROWN']
        if text:
            it.npc('OBJ_EVENT_GFX_WOMAN_2' if 'House' in name else 'OBJ_EVENT_GFX_MAN_4', 4, 4 if 'House' in name or 'Radio' in name or 'Flower' in name else 5, text)
        t.interiors.append(it)
    return t


def delta():
    """The mouth of the Lethys."""
    W, H = 52, 18
    g = Grid(W, H, '≈')
    g.rect(0, 0, 11, 3, 'b').trees(0, 0, 5, 1).rect(14, 6, 22, 8, 'b').rect(34, 10, 41, 12, 'b')
    t = Town('LethysDelta', g, secondary='gTileset_Mauville', mapsec='MAPSEC_ROUTE_107', music='MUS_ROUTE104', map_type='MAP_TYPE_ROUTE')
    t.npc('OBJ_EVENT_GFX_FISHERMAN', 18, 7, 'The LETHYS DELTA. Everything the river carries ends up here.', move='MOVEMENT_TYPE_FACE_DOWN')
    return t


def beach():
    """Valecrown Beach, south of the capital."""
    W, H = 72, 14
    g = Grid(W, H, '≈')
    g.rect(0, 0, W - 1, 5, 'b').rect(20, 6, 40, 6, 'b')
    t = Town('ValecrownBeach', g, secondary='gTileset_Mauville', mapsec='MAPSEC_ROUTE_108', music='MUS_ROUTE104', map_type='MAP_TYPE_ROUTE')
    t.npc('OBJ_EVENT_GFX_TUBER_F', 30, 3, 'The sea is so warm today!', move='MOVEMENT_TYPE_WANDER_AROUND', rx=3, ry=1)
    t.npc('OBJ_EVENT_GFX_SWIMMER_M', 50, 9, 'Beyond the beach there is nothing but sea. Kaldria is all there is!', move='MOVEMENT_TYPE_WANDER_AROUND', rx=3, ry=2)
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

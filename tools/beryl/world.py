"""Kaldria: every generated map. Run `python3 tools/beryl/world.py` to (re)write them,
`python3 tools/beryl/world.py --render DIR` to also save a PNG of each outdoor map."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kaldria import Grid, Town, Interior, pokecenter, mart, Project  # noqa: E402
import render  # noqa: E402

PROJ = Project()
# Hoenn place-name slots reused for Kaldria places
MAPSEC_NAMES = {
    'MAPSEC_LITTLEROOT_TOWN': 'STILLBROOK',
    'MAPSEC_ROUTE_101': 'ROUTE 1',
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
    for y in range(20, H):
        x0 = max(36, 46 - (y - 20) // 2)
        g.rect(x0, y, W - 1, y, '~')
    g.trees(34, 14, 47, 19)
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
        g.rect(36 + 2 * y, y, W - 1, y, '~')
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


# Where each outdoor map sits in the world, in tiles (see docs/beryl/WORLD_MAP.md).
WORLD = {
    'Stillbrook': (0, 136),
    'KaldriaRoute1': (0, 180),
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


def main():
    towns = [stillbrook(), route1()]
    link(towns)
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

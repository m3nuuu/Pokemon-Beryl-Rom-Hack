"""Beryl map generator.

Maps are drawn as ASCII art, one character per metatile, and turned into
Porymap-compatible layouts (map.bin/border.bin), map.json and scripts.inc.
Terrain edges (trees, water, paths) are filled in automatically from rules
learned from the FireRed/LeafGreen (Kanto) maps, so the art only says *what* is where.
Everything is built on gTileset_General_Frlg and is part of the `make firered` build.

See tools/beryl/README.md for the character legend.
"""
import collections, json, os, struct, sys
from functools import lru_cache

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render  # noqa: E402

ROOT = render.ROOT
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.cache')

COLL = 1 << 10
def blk(mid, coll=0, elev=3):
    return mid | (coll << 10) | (elev << 12)


# ---------------------------------------------------------------- metatile info
@lru_cache(None)
def behaviors():
    names = [l.strip().rstrip(',').split()[0] for l in open(os.path.join(ROOT, 'include/constants/metatile_behaviors.h')) if l.strip().startswith('MB_')]
    raw = open(os.path.join(ROOT, 'data/tilesets/primary/general_frlg/metatile_attributes.bin'), 'rb').read()
    attrs = struct.unpack(f'<{len(raw) // 4}I', raw)
    return [names[a & 0x1FF] if (a & 0x1FF) < len(names) else 'MB_INVALID' for a in attrs]


PRIMARY = 'gTileset_General_Frlg'
NPRI = 640  # metatiles in a FRLG primary tileset; secondary ids start here


WATER_POND = {'MB_POND_WATER'}
WATER_SEA = {'MB_OCEAN_WATER', 'MB_DEEP_WATER'}


def is_pond(mid):
    return mid < NPRI and behaviors()[mid] in WATER_POND


def is_sea(mid):
    return mid < NPRI and behaviors()[mid] in WATER_SEA


# sandy path with grass edges, and its inner corners
PATH_IDS = {0x0D3, 0x0D4, 0x0D5, 0x0DB, 0x0DC, 0x0DD, 0x0E3, 0x0E4, 0x0E5, 0x102, 0x103, 0x104, 0x105}
# the plain sand patches (no grass rim inside), used as dirt
DIRT_IDS = {0x0D0, 0x0D1, 0x0D2, 0x0D8, 0x0D9, 0x0DA, 0x0E0, 0x0E1, 0x0E2}
# light grey paving of the Kanto towns
PAVE_IDS = {0x165, 0x166, 0x167, 0x16D, 0x16E, 0x16F, 0x175, 0x176, 0x177, 0x195, 0x196, 0x19D, 0x19E}
ROAD_IDS = PAVE_IDS
ROCK_IDS = set(range(0x068, 0x0B0)) - {0x074, 0x089, 0x091, 0x0A9, 0x087, 0x08F, 0x097}


def is_rock(mid):
    return mid in ROCK_IDS and behaviors()[mid] not in WATER_POND


# ---------------------------------------------------------------- learning
def corpus():
    for lay in render.layouts().values():
        if lay.get('primary_tileset') != PRIMARY or '_Frlg/' not in lay['blockdata_filepath']:
            continue
        try:
            yield lay, render.read_blocks(lay)
        except FileNotFoundError:
            continue


GROUNDISH = {0x001, 0x004, 0x005, 0x008, 0x009, 0x010, 0x011, 0x00D, 0x115} | PATH_IDS
N8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]


def norm_mask(m):
    """Drop corner bits that cannot matter (blob-47 style)."""
    nw, n, ne, w, e, sw, s, se = [(m >> i) & 1 for i in range(8)]
    nw &= n & w; ne &= n & e; sw &= s & w; se &= s & e
    return sum(b << i for i, b in enumerate([nw, n, ne, w, e, sw, s, se]))


def mask_at(get, x, y, deep=False):
    m = norm_mask(sum((1 << i) for i, (dx, dy) in enumerate(N8) if get(x + dx, y + dy)))
    if deep:  # cliffs need to know about the row two below too
        m |= (1 << 8) if get(x, y + 2) else 0
    return m


@lru_cache(None)
def learned():
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, 'learned_frlg.json')
    if os.path.exists(path):
        d = json.load(open(path))
        return {k: {int(m): v for m, v in t.items()} for k, t in d['classes'].items()}, {int(k): v for k, v in d['bits'].items()}
    classes = {'pond': is_pond, 'sea': is_sea, 'path': PATH_IDS.__contains__, 'dirt': DIRT_IDS.__contains__, 'rock': is_rock,
               'pave': PAVE_IDS.__contains__, 'road': ROAD_IDS.__contains__}
    tables = {k: collections.defaultdict(collections.Counter) for k in classes}
    bits = collections.defaultdict(collections.Counter)
    for lay, b in corpus():
        w, h = lay['width'], lay['height']
        ids = [v & 0x3FF for v in b]
        for i, v in enumerate(b):
            bits[v & 0x3FF][v >> 10] += 1
        for name, pred in classes.items():
            mem = [pred(m) for m in ids]
            def get(x, y):
                return mem[min(max(y, 0), h - 1) * w + min(max(x, 0), w - 1)]
            for i, m in enumerate(ids):
                if mem[i] and m < NPRI:
                    x, y = i % w, i // w
                    if name in ('pond', 'sea'):
                        # learn shores only from water that meets plain ground
                        nb = [ids[min(max(y + dy, 0), h - 1) * w + min(max(x + dx, 0), w - 1)] for dx, dy in N8]
                        if any(not pred(n) and n not in GROUNDISH for n in nb):
                            continue
                    tables[name][mask_at(get, x, y, name == 'rock')][m] += 1
    out = {k: {m: c.most_common(1)[0][0] for m, c in t.items()} for k, t in tables.items()}
    bitmode = {m: c.most_common(1)[0][0] for m, c in bits.items()}
    json.dump({'classes': {k: {str(m): v for m, v in t.items()} for k, t in out.items()}, 'bits': {str(k): v for k, v in bitmode.items()}}, open(path, 'w'))
    return out, bitmode


def autotile(cls, mask, fallback):
    table = learned()[0][cls]
    if mask in table:
        return table[mask]
    # nearest known mask by differing bits, preferring the orthogonal ones
    best, score = None, 99
    for m, v in table.items():
        d = bin(m ^ mask).count('1') + 2 * bin((m ^ mask) & 0b01011010).count('1')
        if d < score:
            best, score = v, d
    return best if best is not None else fallback


# ---------------------------------------------------------------- stamps
class Stamp:
    """A building copied from a Kanto map. `secondary` is the tileset it needs (None: primary only)."""
    def __init__(self, layout, x, y, w, h, door=None, secondary=None):
        self.layout, self.x, self.y, self.w, self.h, self.door = layout, x, y, w, h, door
        self.secondary = secondary

    @lru_cache(None)
    def blocks(self):
        lay = render.layouts()[self.layout]
        b = render.read_blocks(lay)
        return [[b[(self.y + j) * lay['width'] + self.x + i] for i in range(self.w)] for j in range(self.h)]


PALLET, VIRIDIAN, PEWTER, CERULEAN = 'gTileset_PalletTown', 'gTileset_ViridianCity', 'gTileset_PewterCity', 'gTileset_CeruleanCity'
LAVENDER, VERMILION, CELADON, FUCHSIA = 'gTileset_LavenderTown', 'gTileset_VermilionCity', 'gTileset_CeladonCity', 'gTileset_FuchsiaCity'
SEVII45 = 'gTileset_SeviiIslands45'
# Pallet Town's tiles with its pale lawn recoloured to ordinary grass (data/tilesets/secondary/stillbrook)
STILLBROOK = 'gTileset_Stillbrook'
SAME_TILES = {STILLBROOK: PALLET}

# name: Stamp(layout, x, y, w, h, door offset, secondary)
STAMPS = {
    # primary tileset: usable in every town
    'pokecenter': Stamp('LAYOUT_PEWTER_CITY', 15, 21, 5, 5, (2, 4)),
    'mart': Stamp('LAYOUT_VIRIDIAN_CITY', 34, 16, 4, 4, (2, 3)),
    'gym': Stamp('LAYOUT_PEWTER_CITY', 12, 12, 7, 5, (3, 4)),
}


def stamp(name, *a, **k):
    STAMPS[name] = Stamp(*a, **k)


# small grey gate house (the Underground Path entrances); primary tiles too
stamp('gate', 'LAYOUT_ROUTE5', 30, 28, 4, 4, (1, 3))
# Pallet Town: red-roofed houses, the lab, a mailbox
stamp('home', 'LAYOUT_PALLET_TOWN', 5, 3, 5, 5, (1, 4), secondary=PALLET)
stamp('lab', 'LAYOUT_PALLET_TOWN', 13, 9, 7, 5, (3, 4), secondary=PALLET)
stamp('mailbox', 'LAYOUT_PALLET_TOWN', 4, 6, 1, 2, None, secondary=PALLET)
# Vermilion City: harbour houses on sand
stamp('verm_house', 'LAYOUT_VERMILION_CITY', 18, 14, 4, 4, (1, 3), secondary=VERMILION)
stamp('verm_hall', 'LAYOUT_VERMILION_CITY', 11, 14, 5, 4, (1, 3), secondary=VERMILION)
# Celadon City: department store, game corner, prize house, apartment block
stamp('dept_store', 'LAYOUT_CELADON_CITY', 9, 5, 9, 10, (2, 9), secondary=CELADON)
stamp('casino', 'LAYOUT_CELADON_CITY', 31, 17, 7, 5, (3, 4), secondary=CELADON)
stamp('prize', 'LAYOUT_CELADON_CITY', 38, 17, 3, 4, (1, 3), secondary=CELADON)
stamp('apartment', 'LAYOUT_CELADON_CITY', 36, 25, 4, 5, (1, 4), secondary=CELADON)
# Lavender Town: the tower, purple houses; Route 10's power plant uses the same set
stamp('tower', 'LAYOUT_LAVENDER_TOWN', 15, 0, 7, 7, (3, 6), secondary=LAVENDER)
stamp('lav_house', 'LAYOUT_LAVENDER_TOWN', 8, 8, 5, 4, (2, 3), secondary=LAVENDER)
stamp('power_plant', 'LAYOUT_ROUTE10', 2, 35, 11, 7, (5, 5), secondary=LAVENDER)

# ---------------------------------------------------------------- canvas
GRASS4 = ((0x008, 0x009), (0x010, 0x011))   # the 2x2 grass texture
GRASS, TALL, FLOWER = 0x008, 0x00D, 0x004
SIGN = 0x003
LEDGE_L, LEDGE, LEDGE_R = 0x0B0, 0x087, 0x0B1
SAND = 0x115
CAVE = 0x0A9
STAIRS_L, STAIRS_R = 0x091, 0x089
FALL_TOP, FALL, FALL_FOOT = 0x127, 0x12F, 0x137
# FRLG trees: 2x2, top half drawn over the bottom half of the tree above
TREE_T, TREE_T_OPEN = (0x01C, 0x01D), (0x01E, 0x01F)
TREE_B, TREE_B_OPEN = (0x014, 0x015), (0x016, 0x017)
TREE_END, TREE_END_OPEN = (0x024, 0x025), (0x026, 0x027)
CANOPY, CANOPY_TALL = (0x00E, 0x00F), (0x00B, 0x00C)


def grass(x, y):
    return GRASS4[y & 1][x & 1]


class MapArt:
    """One map: ASCII terrain + buildings + events."""

    def __init__(self, name, art, stamps=(), primary=PRIMARY, secondary=PALLET):
        rows = [r for r in art.strip('\n').split('\n')]
        self.h, self.w = len(rows), max(len(r) for r in rows)
        self.chars = [list(r.ljust(self.w, '.')) for r in rows]
        self.name, self.primary, self.secondary = name, primary, secondary
        self.stamps = list(stamps)  # (stampname, x, y, warp dest or None)
        self.over = {}
        self.doors = []
        self.check_secondary = True

    def c(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.chars[y][x]
        return None

    def build(self):
        w, h = self.w, self.h
        bits = learned()[1]
        out = [blk(grass(i % w, i // w)) for i in range(w * h)]
        put = lambda x, y, v: out.__setitem__(y * w + x, v)
        # plain ground
        for y in range(h):
            for x in range(w):
                ch = self.chars[y][x]
                if ch == ',':
                    put(x, y, blk(TALL))
                elif ch == '*':
                    put(x, y, blk(FLOWER))
                elif ch == 's':
                    put(x, y, blk(SIGN, 1, 0))
                elif ch == 'b':
                    put(x, y, blk(SAND))
        # trees on the 2x2 grid; out-of-map counts as forest
        def tree(cx, cy):
            if cx < 0 or cy < 0 or cx * 2 >= w or cy * 2 >= h:
                return True
            return any(self.c(cx * 2 + i, cy * 2 + j) == 'T' for i in range(2) for j in range(2))
        for cy in range((h + 1) // 2):
            for cx in range((w + 1) // 2):
                if not (cx * 2 < w and cy * 2 < h and tree(cx, cy)):
                    continue
                x, y = cx * 2, cy * 2
                L, R, U, D = tree(cx - 1, cy), tree(cx + 1, cy), tree(cx, cy - 1), tree(cx, cy + 1)
                top = (TREE_T[0] if L and U else TREE_T_OPEN[0], TREE_T[1] if R and U else TREE_T_OPEN[1])
                if D:
                    bot = (TREE_B[0] if L else TREE_B_OPEN[0], TREE_B[1] if R else TREE_B_OPEN[1])
                else:
                    bot = (TREE_END[0] if L else TREE_END_OPEN[0], TREE_END[1] if R else TREE_END_OPEN[1])
                for i in range(2):
                    if x + i < w:
                        put(x + i, y, blk(top[i], 1, 0))
                        if y + 1 < h:
                            put(x + i, y + 1, blk(bot[i], 1, 0))
                # canopy over the row above when it is open ground
                if not U and y - 1 >= 0:
                    for i in range(2):
                        ch = self.c(x + i, y - 1)
                        if ch in ('.', ',', '*'):
                            put(x + i, y - 1, blk((CANOPY_TALL if ch == ',' else CANOPY)[i], 0, 3))
        # autotiled classes
        for cls, ch, coll, elev, fb in (('pond', '~', 0, 1, 0x1A4), ('sea', '≈', 0, 1, 0x1D9), ('path', '=', 0, 3, 0x0DC),
                                        ('dirt', ':', 0, 3, 0x0D9), ('rock', '^', 1, 0, 0x071), ('pave', 'p', 0, 3, 0x16E), ('road', 'R', 0, 3, 0x16E)):
            members = {'^': ('^', 'C', 'S', 'W'), '~': ('~', '≈'), '≈': ('~', '≈')}.get(ch, (ch,))
            get = lambda x, y, members=members: self.c(min(max(x, 0), w - 1), min(max(y, 0), h - 1)) in members
            for y in range(h):
                for x in range(w):
                    if self.chars[y][x] == ch:
                        m = autotile(cls, mask_at(get, x, y, cls == 'rock'), fb)
                        if cls == 'rock':  # cliffs: keep whatever collision the corpus uses for that piece
                            put(x, y, (m | (bits.get(m, 1) << 10)))
                        else:
                            put(x, y, blk(m, coll, elev))
        # cave entrances, stairs, waterfalls
        for y in range(h):
            for x in range(w):
                ch = self.chars[y][x]
                if ch == 'C':
                    put(x, y, blk(CAVE, 1, 0))
                elif ch == 'S':  # stairs through a cliff, two wide
                    put(x, y, blk(STAIRS_R if self.c(x - 1, y) == 'S' else STAIRS_L, 0, 3))
                elif ch == 'W':
                    top = self.c(x, y - 1) != 'W'
                    foot = self.c(x, y + 1) != 'W'
                    put(x, y, blk(FALL_TOP if top else (FALL_FOOT if foot else FALL), 0, 1))
        # ledges: runs of '_' (jump south)
        for y in range(h):
            for x in range(w):
                if self.chars[y][x] == '_':
                    l, r = self.c(x - 1, y) == '_', self.c(x + 1, y) == '_'
                    m = LEDGE if (l and r) else (LEDGE_R if l else LEDGE_L if r else LEDGE)
                    put(x, y, blk(m, 1, 0))
        # buildings
        for i, (sname, sx, sy, dest) in enumerate(self.stamps):
            st = STAMPS[sname]
            if self.check_secondary and st.secondary and st.secondary != SAME_TILES.get(self.secondary, self.secondary):
                raise ValueError(f'{self.name}: stamp {sname} needs {st.secondary}, map uses {self.secondary}')
            for j, row in enumerate(st.blocks()):
                for k, v in enumerate(row):
                    if sx + k < w and sy + j < h:
                        put(sx + k, sy + j, v)
            if st.door and dest:
                self.doors.append((sx + st.door[0], sy + st.door[1], dest))
        for (x, y), v in self.over.items():
            put(x, y, v)
        return out


def write_bin(path, blocks):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'wb').write(struct.pack(f'<{len(blocks)}H', *blocks))


# ---------------------------------------------------------------- output
def upper_id(name):
    import re
    s = re.sub(r'(?<=[a-z])(?=[A-Z])', '_', name)
    return s.replace('__', '_').upper()


GROUP_OUT, GROUP_IN = 'gMapGroup_KaldriaOutdoor', 'gMapGroup_KaldriaIndoor'


class Project:
    """Collects generated maps and writes them into the repo in one go."""

    def __init__(self):
        self.maps = []        # dicts ready for map.json
        self.layouts = []     # layout entries
        self.scripts = {}     # name -> scripts.inc text
        self.heal = []
        self.mapsec_names = {}  # Hoenn MAPSEC reused for a Kaldria place -> its new name

    # -- layouts
    def add_layout(self, name, w, h, blocks, primary, secondary, border=(0x01C, 0x01D, 0x014, 0x015)):
        lid = 'LAYOUT_' + upper_id(name)
        d = f'data/layouts/{name}'
        write_bin(os.path.join(ROOT, d, 'map.bin'), blocks)
        write_bin(os.path.join(ROOT, d, 'border.bin'), [blk(b, 1, 0) for b in border])
        self.layouts.append({'id': lid, 'name': f'{name}_Layout', 'width': w, 'height': h, 'primary_tileset': primary,
                             'secondary_tileset': secondary, 'border_filepath': f'{d}/border.bin',
                             'blockdata_filepath': f'{d}/map.bin', 'layout_version': 'frlg',
                             'border_width': 2, 'border_height': 2})
        return lid

    def add_map(self, m, group, scripts=''):
        m.setdefault('connections', None)
        for k in ('object_events', 'warp_events', 'coord_events', 'bg_events'):
            m.setdefault(k, [])
        self.maps.append((group, m))
        self.scripts[m['name']] = scripts

    def write(self):
        # forget maps and layouts an earlier run made that are no longer generated
        import re, shutil
        inc = os.path.join(ROOT, 'data/maps/kaldria_scripts.inc')
        old = re.findall(r'data/maps/(\w+)/scripts.inc', open(inc).read()) if os.path.exists(inc) else []
        names = {m['name'] for _, m in self.maps}
        for n in old:
            if n not in names and os.path.isdir(os.path.join(ROOT, 'data/maps', n)):
                shutil.rmtree(os.path.join(ROOT, 'data/maps', n))
        # layouts.json: replace our previous entries, keep the rest
        lp = os.path.join(ROOT, 'data/layouts/layouts.json')
        lj = json.load(open(lp))
        ours = {l['id'] for l in self.layouts}
        lj['layouts'] = [l for l in lj['layouts'] if l.get('id') not in ours] + self.layouts
        json.dump(lj, open(lp, 'w'), indent=2, ensure_ascii=False)
        open(lp, 'a').write('\n')
        # map groups
        gp = os.path.join(ROOT, 'data/maps/map_groups.json')
        gj = json.load(open(gp))
        for g in (GROUP_OUT, GROUP_IN):
            if g not in gj['group_order']:
                gj['group_order'].append(g)
            gj[g] = []
        for group, m in self.maps:
            gj[group].append(m['name'])
        json.dump(gj, open(gp, 'w'), indent=2, ensure_ascii=False)
        open(gp, 'a').write('\n')
        for group, m in self.maps:
            d = os.path.join(ROOT, 'data/maps', m['name'])
            os.makedirs(d, exist_ok=True)
            json.dump(m, open(os.path.join(d, 'map.json'), 'w'), indent=2, ensure_ascii=False)
            open(os.path.join(d, 'map.json'), 'a').write('\n')
            open(os.path.join(d, 'scripts.inc'), 'w').write(self.scripts[m['name']])
        open(os.path.join(ROOT, 'data/maps/kaldria_scripts.inc'), 'w').write(
            '@ Generated by tools/beryl/world.py\n' + ''.join(f'\t.include "data/maps/{m["name"]}/scripts.inc"\n' for _, m in self.maps))
        # place names shown on entering a map
        rp = os.path.join(ROOT, 'src/data/region_map/region_map_sections.json')
        rj = json.load(open(rp))
        for sec in rj['map_sections']:
            if sec['id'] in self.mapsec_names:
                sec['name'] = self.mapsec_names[sec['id']]
        json.dump(rj, open(rp, 'w'), indent=2, ensure_ascii=False)
        open(rp, 'a').write('\n')
        # heal locations
        hp = os.path.join(ROOT, 'src/data/heal_locations.json')
        hj = json.load(open(hp))
        ids = {h['id'] for h in self.heal}
        hj['heal_locations'] = [h for h in hj['heal_locations'] if h['id'] not in ids] + self.heal
        json.dump(hj, open(hp, 'w'), indent=2, ensure_ascii=False)
        open(hp, 'a').write('\n')

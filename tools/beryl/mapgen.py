"""Beryl map generator.

Maps are drawn as ASCII art, one character per metatile, and turned into
Porymap-compatible layouts (map.bin/border.bin), map.json and scripts.inc.
Terrain edges (trees, water, paths) are filled in automatically from rules
learned from the Hoenn maps, so the art only says *what* is where.

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
    raw = open(os.path.join(ROOT, 'data/tilesets/primary/general/metatile_attributes.bin'), 'rb').read()
    attrs = struct.unpack(f'<{len(raw) // 2}H', raw)
    return [names[a & 0xFF] for a in attrs]


WATER_POND = {'MB_POND_WATER'}
WATER_SEA = {'MB_OCEAN_WATER', 'MB_DEEP_WATER'}


def is_pond(mid):
    return mid < 512 and behaviors()[mid] in WATER_POND


def is_sea(mid):
    return mid < 512 and behaviors()[mid] in WATER_SEA


PATH_IDS = {0x118, 0x119, 0x11A, 0x120, 0x121, 0x122, 0x128, 0x129, 0x12A}
DIRT_IDS = {0x1D0, 0x1D1, 0x1D2, 0x1D8, 0x1D9, 0x1DA, 0x1E0, 0x1E1, 0x1E2}
PAVE_IDS = {0x3D, 0x3E, 0x3F, 0x4D, 0x4E, 0x4F, 0x5D, 0x5E, 0x5F, 0x65, 0x66, 0x67, 0x45, 0x46, 0x47, 0x55, 0x56, 0x57}
ROAD_IDS = {0x100, 0x101, 0x102, 0x108, 0x10A, 0x110, 0x111, 0x112, 0x05E}
ROCK_IDS = set(range(0x068, 0x0B0)) - {0x0A1, 0x0A7} | {0x0E1}


def is_rock(mid):
    return mid in ROCK_IDS and behaviors()[mid] not in WATER_POND


# ---------------------------------------------------------------- learning
def corpus():
    for lay in render.layouts().values():
        if lay.get('primary_tileset') != 'gTileset_General':
            continue
        try:
            yield lay, render.read_blocks(lay)
        except FileNotFoundError:
            continue


GROUNDISH = {0x001, 0x00D, 0x004, 0x015, 0x124} | PATH_IDS
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
    path = os.path.join(CACHE, 'learned.json')
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
                if mem[i] and m < 512:
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
    def __init__(self, layout, x, y, w, h, door=None, pad=None):
        self.layout, self.x, self.y, self.w, self.h, self.door = layout, x, y, w, h, door

    @lru_cache(None)
    def blocks(self):
        lay = render.layouts()[self.layout]
        b = render.read_blocks(lay)
        return [[b[(self.y + j) * lay['width'] + self.x + i] for i in range(self.w)] for j in range(self.h)]


# Footprint letter -> stamp. Size of the letter block in the art must match.
STAMPS = {
    # name: Stamp(layout, x, y, w, h, door offset)
    'pokecenter': Stamp('LAYOUT_PETALBURG_CITY', 19, 13, 4, 4, (1, 3)),
    'mart': Stamp('LAYOUT_MAUVILLE_CITY', 22, 11, 4, 4, (1, 3)),
    'gym': Stamp('LAYOUT_PETALBURG_CITY', 12, 4, 6, 5, (3, 4)),
    'house4': Stamp('LAYOUT_PETALBURG_CITY', 9, 16, 4, 4, (1, 3)),
    'house5': Stamp('LAYOUT_PETALBURG_CITY', 5, 2, 5, 4, (2, 3)),
    'home': Stamp('LAYOUT_LITTLEROOT_TOWN', 2, 4, 5, 5, (3, 4)),
    'home_b': Stamp('LAYOUT_LITTLEROOT_TOWN', 13, 4, 5, 5, (1, 4)),
    'lab': Stamp('LAYOUT_LITTLEROOT_TOWN', 3, 12, 7, 5, (4, 4)),
    'cottage': Stamp('LAYOUT_OLDALE_TOWN', 4, 4, 4, 4, (1, 3)),
    # gTileset_Mauville
    'mv_house': Stamp('LAYOUT_MAUVILLE_CITY', 18, 11, 4, 4, (1, 3)),
    'mv_house5': Stamp('LAYOUT_MAUVILLE_CITY', 31, 11, 5, 4, (1, 3)),
    'mv_bikeshop': Stamp('LAYOUT_MAUVILLE_CITY', 34, 2, 5, 4, (1, 3)),
    'mv_gamecorner': Stamp('LAYOUT_MAUVILLE_CITY', 5, 10, 7, 4, (3, 3)),
    'mv_tower': Stamp('LAYOUT_MAUVILLE_CITY', 36, 11, 4, 5, None),
    # gTileset_Fortree
    'institute': Stamp('LAYOUT_ROUTE119', 1, 26, 11, 8, (5, 6)),
}

# ---------------------------------------------------------------- canvas
GRASS, TALL, FLOWER = 0x001, 0x00D, 0x004
TREE_TL, TREE_TR, TREE_TL_E, TREE_TR_E = 0x1D4, 0x1D5, 0x1D6, 0x1D7
TREE_BL, TREE_BR = 0x1DC, 0x1DD
TREE_BL_END, TREE_BR_END, TREE_BL_ENDE, TREE_BR_ENDE = 0x1E4, 0x1E5, 0x1E6, 0x1E7
CANOPY_L, CANOPY_R, CANOPY_TALL_L, CANOPY_TALL_R = 0x1CE, 0x1CF, 0x1C6, 0x1C7
LEDGE_L, LEDGE, LEDGE_R = 0x0D5, 0x087, 0x0D6
SIGN = 0x003


class MapArt:
    """One map: ASCII terrain + buildings + events."""

    LEGEND = {
        '.': 'grass', ',': 'tall', '*': 'flower', 'T': 'tree', '~': 'pond', '≈': 'sea',
        '=': 'path', ':': 'dirt', '_': 'ledge', 's': 'sign', '#': 'stamp',
    }

    def __init__(self, name, art, stamps=(), primary='gTileset_General', secondary='gTileset_Petalburg'):
        rows = [r for r in art.strip('\n').split('\n')]
        self.h, self.w = len(rows), max(len(r) for r in rows)
        self.chars = [list(r.ljust(self.w, '.')) for r in rows]
        self.name, self.primary, self.secondary = name, primary, secondary
        self.stamps = list(stamps)  # (stampname, x, y, warp dest or None)
        self.over = {}
        self.doors = []  # (x, y, stampname, index)

    def c(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.chars[y][x]
        return None

    def build(self):
        w, h = self.w, self.h
        out = [blk(GRASS) for _ in range(w * h)]
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
                    put(x, y, blk(0x124, 0, 3))
        # trees on the 2x2 grid; out-of-map counts as forest
        def tree(cx, cy):
            if cx < 0 or cy < 0 or cx * 2 >= w or cy * 2 >= h:
                return True
            return any(self.c(cx * 2 + i, cy * 2 + j) == 'T' for i in range(2) for j in range(2))
        def tree_in(cx, cy):
            return 0 <= cx * 2 < w and 0 <= cy * 2 < h and tree(cx, cy)
        for cy in range((h + 1) // 2):
            for cx in range((w + 1) // 2):
                if not tree_in(cx, cy):
                    continue
                x, y = cx * 2, cy * 2
                L, R, D = tree(cx - 1, cy), tree(cx + 1, cy), tree(cx, cy + 1)
                tiles = {
                    (0, 0): TREE_TL if L else TREE_TL_E, (1, 0): TREE_TR if R else TREE_TR_E,
                    (0, 1): TREE_BL if D else (TREE_BL_END if L else TREE_BL_ENDE),
                    (1, 1): TREE_BR if D else (TREE_BR_END if R else TREE_BR_ENDE),
                }
                for (i, j), m in tiles.items():
                    if x + i < w and y + j < h:
                        put(x + i, y + j, blk(m, 1, 0))
                # canopy over the row above when it is open ground
                if not tree(cx, cy - 1) and y - 1 >= 0:
                    for i, (a, b) in enumerate([(CANOPY_L, CANOPY_TALL_L), (CANOPY_R, CANOPY_TALL_R)]):
                        ch = self.c(x + i, y - 1)
                        if ch in ('.', ',', '*', '=', ':'):
                            put(x + i, y - 1, blk(b if ch == ',' else a, 0, 3))
        # autotiled classes
        for cls, ch, coll, elev, fb in (('pond', '~', 0, 1, 0x0A1), ('sea', '≈', 0, 1, 0x170), ('path', '=', 0, 3, 0x121),
                                        ('dirt', ':', 0, 3, 0x1D9), ('rock', '^', 1, 0, 0x071), ('pave', 'p', 0, 3, 0x066), ('road', 'R', 0, 3, 0x05E)):
            get = lambda x, y, ch=ch: self.c(min(max(x, 0), w - 1), min(max(y, 0), h - 1)) in (ch, 'C', 'S', 'W') if ch == '^' else \
                self.c(min(max(x, 0), w - 1), min(max(y, 0), h - 1)) == ch
            for y in range(h):
                for x in range(w):
                    if self.chars[y][x] == ch:
                        put(x, y, blk(autotile(cls, mask_at(get, x, y, cls == 'rock'), fb), coll, elev))
        # cave entrances in rock faces
        for y in range(h):
            for x in range(w):
                ch = self.chars[y][x]
                if ch == 'C':
                    put(x, y, blk(0x0A7, 0, 0))
                elif ch == 'S':  # stairs through a cliff, two wide
                    put(x, y, blk(0x0CF if self.c(x - 1, y) == 'S' else 0x0AF, 0, 3))
                elif ch == 'W':  # waterfall; the water below it gets foam
                    top = self.c(x, y - 1) != 'W'
                    left = self.c(x - 1, y) != 'W'
                    put(x, y, blk((0x0BB if left else 0x0B3) if top else 0x0B9, 0, 1))
                    if self.c(x, y + 1) in ('~', '≈'):
                        r = self.c(x + 1, y) != 'W'
                        put(x, y + 1, blk(0x02C if left else (0x03C if r else 0x034), 0, 1))
        # ledges: runs of '_' (jump south)
        for y in range(h):
            for x in range(w):
                if self.chars[y][x] == '_':
                    l, r = self.c(x - 1, y) == '_', self.c(x + 1, y) == '_'
                    m = LEDGE if (l and r) else (LEDGE_R if l else LEDGE_L if r else LEDGE)
                    put(x, y, blk(m, 1, 3))
        # buildings
        for i, (sname, sx, sy, dest) in enumerate(self.stamps):
            st = STAMPS[sname]
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
    def add_layout(self, name, w, h, blocks, primary, secondary, border=(0x1D4, 0x1D5, 0x1DC, 0x1DD)):
        lid = 'LAYOUT_' + upper_id(name)
        d = f'data/layouts/{name}'
        write_bin(os.path.join(ROOT, d, 'map.bin'), blocks)
        write_bin(os.path.join(ROOT, d, 'border.bin'), [blk(b, 1, 0) for b in border])
        self.layouts.append({'id': lid, 'name': f'{name}_Layout', 'width': w, 'height': h, 'primary_tileset': primary,
                             'secondary_tileset': secondary, 'border_filepath': f'{d}/border.bin',
                             'blockdata_filepath': f'{d}/map.bin', 'layout_version': 'emerald'})
        return lid

    def add_map(self, m, group, scripts=''):
        m.setdefault('connections', None)
        for k in ('object_events', 'warp_events', 'coord_events', 'bg_events'):
            m.setdefault(k, [])
        self.maps.append((group, m))
        self.scripts[m['name']] = scripts

    def write(self):
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

"""Valecrown pilot: the capital drawn with Emerald's General tileset and Team Aqua's Brick City.

    python3 tools/beryl/world.py --pilot-valecrown

The map is first made the usual way (FireRed tiles, from the paint), then redrawn:
* ground, water, cliffs, signs: each FireRed metatile becomes the Emerald one that looks most like it
* trees: Emerald's 2x2 trees on the same grid
* streets: Brick City's stone street, with a herringbone pavement and kerbs along it
* buildings: Brick City houses, hall, gym and POKé CENTER, cut from the tileset's example town, each
  placed so its door is where the FireRed building's door was (the warps stay as they are)

Valecrown's neighbours stay on FireRed's tiles, and a map shows its neighbours' edges with its own
tiles, so the strips seen across Valecrown's edges look wrong in this pilot.
"""
import collections, json, os, struct, sys
from functools import lru_cache
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render, mapgen  # noqa: E402
from mapgen import blk, STAMPS  # noqa: E402

E_PRIMARY, E_SECONDARY = 'gTileset_General', 'gTileset_BrickCity'
render.tileset_dirs()[E_SECONDARY] = os.path.join(render.ROOT, 'data/tilesets/secondary/brick_city')
EXAMPLE = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'brick_city_example.json')))['grid']
NPRI_F = 640

# Emerald trees, 2x2: (top-left, top-right), (bottom-left, bottom-right); bottoms with no tree below
E_TREE_T, E_TREE_B = (0x1D4, 0x1D5), (0x1DC, 0x1DD)
E_TREE_END, E_TREE_END_OPEN = (0x1E4, 0x1E5), (0x1E6, 0x1E7)
F_TREE = {0x01C: E_TREE_T[0], 0x01D: E_TREE_T[1], 0x01E: E_TREE_T[0], 0x01F: E_TREE_T[1],
          0x014: E_TREE_B[0], 0x015: E_TREE_B[1], 0x016: E_TREE_B[0], 0x017: E_TREE_B[1],
          0x024: E_TREE_END[0], 0x025: E_TREE_END[1], 0x026: E_TREE_END_OPEN[0], 0x027: E_TREE_END_OPEN[1],
          0x00E: 0x001, 0x00F: 0x001, 0x00B: 0x00D, 0x00C: 0x00D}
E_GRASS, E_LONG_GRASS = 0x001, 0x015
# Brick City street and pavement
STREET, WALK = 0x2BB, 0x301
KERB = {'N': 0x2F9, 'NW': 0x2F8, 'NE': 0x2FA, 'S': 0x309, 'SW': 0x308, 'SE': 0x30A, 'W': 0x300, 'E': 0x302,
        'dSE': 0x310, 'dSW': 0x311, 'dNE': 0x312, 'dNW': 0x313}

# Brick City buildings in the example town: x, y, w, h, door offset (None: you cannot go in)
BC = {
    'bc_house': (18, 10, 5, 6, (2, 5)),
    'bc_low': (12, 29, 5, 5, (2, 4)),
    'bc_twin': (16, 19, 4, 7, (1, 6)),
    'bc_gable': (21, 27, 6, 7, (3, 6)),
    'bc_hall': (37, 17, 10, 8, (4, 7)),
    'bc_row': (52, 27, 9, 6, (2, 5)),
    'bc_gym': (51, 13, 6, 5, (3, 4)),
    'bc_pc': (51, 22, 4, 4, (1, 3)),
}
# Emerald's own POKé MART (Oldale Town), all primary tiles
E_MART = [[0x028, 0x029, 0x029, 0x02B], [0x030, 0x031, 0x032, 0x033], [0x038, 0x039, 0x03A, 0x03B],
          [0x040, 0x041, 0x042, 0x043]]
# FireRed building -> (pilot building, keeps its door)
SWAP = {'pokecenter': 'bc_pc', 'mart': 'e_mart', 'gym': 'bc_gym', 'condo': 'bc_gable', 'apartment': 'bc_low',
        'dept_store': 'bc_hall', 'casino': 'bc_house', 'prize': 'bc_low', 'gate': 'bc_low',
        'block_tall': 'bc_twin', 'block_wide': 'bc_gable'}


# FireRed ground -> Emerald ground, where the look-alike search picks badly
SAME = {0x001: 0x001, 0x008: 0x001, 0x009: 0x001, 0x010: 0x001, 0x011: 0x001, 0x00D: 0x00D, 0x004: 0x004,
        0x005: 0x2A7}
E_WATER = {'~': 0x0A1, '≈': 0x170}


@lru_cache(None)
def e_behaviours():
    names = [l.strip().rstrip(',').split()[0] for l in open(os.path.join(render.ROOT, 'include/constants/metatile_behaviors.h'))
             if l.strip().startswith('MB_')]
    raw = open(os.path.join(render.ROOT, 'data/tilesets/primary/general/metatile_attributes.bin'), 'rb').read()
    return [names[a & 0xFF] for a in struct.unpack(f'<{len(raw) // 2}H', raw)]


@lru_cache(None)
def e_learned():
    """Shore tables learned from Emerald's own maps, like mapgen.learned() does from Kanto's."""
    beh = e_behaviours()
    classes = {'~': lambda m: m < 512 and beh[m] == 'MB_POND_WATER',
               '≈': lambda m: m < 512 and beh[m] in ('MB_OCEAN_WATER', 'MB_DEEP_WATER')}
    ground = {0x001, 0x00D, 0x004}
    tables = {k: collections.defaultdict(collections.Counter) for k in classes}
    for lay in render.layouts().values():
        if lay.get('primary_tileset') != E_PRIMARY or lay.get('layout_version') != 'emerald':
            continue
        try:
            b = render.read_blocks(lay)
        except FileNotFoundError:
            continue
        w, h = lay['width'], lay['height']
        ids = [v & 0x3FF for v in b]
        for k, pred in classes.items():
            mem = [pred(m) for m in ids]
            get = lambda x, y: mem[min(max(y, 0), h - 1) * w + min(max(x, 0), w - 1)]
            for i, m in enumerate(ids):
                if not mem[i]:
                    continue
                x, y = i % w, i // w
                nb = [ids[min(max(y + dy, 0), h - 1) * w + min(max(x + dx, 0), w - 1)] for dx, dy in mapgen.N8]
                if any(not pred(n) and n not in ground for n in nb):
                    continue
                tables[k][mapgen.mask_at(get, x, y)][m] += 1
    return {k: {m: c.most_common(1)[0][0] for m, c in t.items()} for k, t in tables.items()}


def e_autotile(cls, mask):
    table = e_learned()[cls]
    if mask in table:
        return table[mask]
    best = min(table, key=lambda m: bin(m ^ mask).count('1') + 2 * bin((m ^ mask) & 0b01011010).count('1'))
    return table[best]


def stamp_blocks(name):
    if name == 'e_mart':
        rows, door = E_MART, (1, 3)
    else:
        x, y, w, h, door = BC[name]
        rows = [EXAMPLE[y + j][x:x + w] for j in range(h)]
    return [[blk(m, 0 if (i, j) == door else 1, 0 if (i, j) == door else 3) for i, m in enumerate(r)]
            for j, r in enumerate(rows)], door


def images(primary, secondary, ids):
    return np.stack([np.asarray(render.metatile_image(primary, secondary, m).convert('RGB'), dtype=np.int32).reshape(-1)
                     for m in ids])


def look_alike(src_secondary, src_ids):
    """FireRed metatile -> the Emerald General metatile that looks most like it."""
    dst_ids = list(range(512))
    dst = images(E_PRIMARY, E_SECONDARY, dst_ids)
    src = images(mapgen.PRIMARY, src_secondary, src_ids)
    out = {}
    for m, im in zip(src_ids, src):
        out[m] = dst_ids[int(np.abs(dst - im[None, :]).sum(1).argmin())]
    return out


def redraw(c, town, proj):
    r = town.region
    w, h = r.w, r.h
    old = c.slice(town.name)
    ch = [[c.g[r.y + j][r.x + i] for i in range(w)] for j in range(h)]
    # buildings in this map, in local coordinates
    olds = [(n, x - r.x, y - r.y) for n, x, y, _ in c.stamps if r.has(x, y)]
    covered = {(x + i, y + j) for n, x, y in olds for j in range(STAMPS[n].h) for i in range(STAMPS[n].w)}
    ids = sorted({v & 0x3FF for k, v in enumerate(old) if (k % w, k // w) not in covered and (v & 0x3FF) not in F_TREE})
    table = look_alike(town.secondary, ids)
    imports = mapgen.IMPORTED
    out = []
    for k, v in enumerate(old):
        m, bits = v & 0x3FF, v & ~0x3FF
        if (k % w, k // w) in covered:
            out.append(blk(E_GRASS))
        elif m in F_TREE:
            out.append(F_TREE[m] | bits)
        elif m == imports['long_grass']:
            out.append(blk(E_LONG_GRASS))
        elif m in SAME:
            out.append(SAME[m] | bits)
        else:
            out.append(table[m] | bits)
    put = lambda x, y, v: out.__setitem__(y * w + x, v) if 0 <= x < w and 0 <= y < h else None
    # water: shores learned from Emerald's maps
    for y in range(h):
        for x in range(w):
            if ch[y][x] in E_WATER:
                memb = lambda a, b: ch[min(max(b, 0), h - 1)][min(max(a, 0), w - 1)] in E_WATER
                put(x, y, blk(e_autotile(ch[y][x], mapgen.mask_at(memb, x, y)), 0, 1))
    # new buildings, doors where the old doors were
    rects = []
    for n, x, y in olds:
        st = STAMPS[n]
        new = SWAP.get(n)
        assert new, f'pilot: no Brick City building for {n}'
        rows, door = stamp_blocks(new)
        nw, nh = len(rows[0]), len(rows)
        if st.door:
            dx, dy = x + st.door[0], y + st.door[1]
            nx, ny = dx - door[0], dy - door[1]
        else:
            nx, ny = x + (st.w - nw) // 2, y + st.h - nh
        rects.append((n, new, nx, ny, nw, nh, rows))
    taken = set()
    for n, new, nx, ny, nw, nh, rows in rects:
        cells = {(nx + i, ny + j) for j in range(nh) for i in range(nw)}
        if cells & taken or not all(0 <= a < w and 0 <= b < h for a, b in cells):
            print(f'pilot: {new} for {n} at {nx + r.x},{ny + r.y} overlaps or leaves the map')
        taken |= cells
    # streets, with a pavement around them on open ground
    street = {(x, y) for y in range(h) for x in range(w) if ch[y][x] == 'K'}
    open_ground = lambda x, y: 0 <= x < w and 0 <= y < h and ch[y][x] in '.,*pV' and (x, y) not in taken
    walk = {(x + dx, y + dy) for x, y in street for dx in (-1, 0, 1) for dy in (-1, 0, 1)
            if open_ground(x + dx, y + dy) and (x + dx, y + dy) not in street}
    walk |= {(x, y) for y in range(h) for x in range(w) if ch[y][x] == 'p' and (x, y) not in taken}
    for x, y in street:
        put(x, y, blk(STREET))
    for x, y in walk:
        s = lambda dx, dy: (x + dx, y + dy) in street
        n, so, we, ea = s(0, -1), s(0, 1), s(-1, 0), s(1, 0)
        key = ('N' if n else 'S' if so else '') + ('W' if we else 'E' if ea else '')
        if not key:
            key = 'dSE' if s(1, 1) else 'dSW' if s(-1, 1) else 'dNE' if s(1, -1) else 'dNW' if s(-1, -1) else ''
        put(x, y, blk(KERB.get(key, WALK)))
    for n, new, nx, ny, nw, nh, rows in rects:
        for j, row in enumerate(rows):
            for i, v in enumerate(row):
                put(nx + i, ny + j, v)
    # the layout: same name, Emerald format
    lay = next(l for l in proj.layouts if l['id'] == town.layout_id)
    mapgen.write_bin(os.path.join(render.ROOT, lay['blockdata_filepath']), out)
    mapgen.write_bin(os.path.join(render.ROOT, lay['border_filepath']), [blk(m, 1, 0) for m in (*E_TREE_T, *E_TREE_B)])
    lay.update({'primary_tileset': E_PRIMARY, 'secondary_tileset': E_SECONDARY, 'layout_version': 'emerald', 'all_versions': True})
    return out

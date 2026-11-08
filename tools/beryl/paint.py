"""The painted map: south Kaldria as a picture, one pixel per tile, that Manuel edits in any paint program.

    python3 tools/beryl/world.py --export-paint DIR      write the template, colour key and guide to DIR
    python3 tools/beryl/world.py --export-paint DIR --fresh   ...ignoring the painting in the repo

When tools/beryl/kaldria_south.png exists, world.py builds the ground from it instead of from the code:
every pixel's colour says what the tile is (see COLOURS), each building is a block of its own colour
(tools/beryl/kaldria_south_key.json says which), and mailboxes, fences, picket fences, bridges and bushes
are painted too. People, signs and the insides of buildings still come from world.py.
"""
import json, os
from PIL import Image, ImageDraw
from mapgen import STAMPS, blk

HERE = os.path.dirname(os.path.abspath(__file__))
PAINT = os.path.join(HERE, 'kaldria_south.png')
KEY = os.path.join(HERE, 'kaldria_south_key.json')

# ground: canvas character -> (colour, name)
COLOURS = {
    '.': ((120, 200, 100), 'grass'),
    ',': ((40, 130, 50), 'tall grass (wild POKéMON)'),
    '*': ((200, 90, 150), 'flowers'),
    'T': ((20, 80, 30), 'trees'),
    '^': ((150, 100, 60), 'cliff / rock'),
    '~': ((70, 130, 230), 'river / lake water'),
    '≈': ((20, 50, 160), 'sea water'),
    '=': ((230, 210, 120), 'path'),
    'p': ((185, 185, 195), 'paving'),
    'b': ((240, 230, 170), 'sand'),
    ':': ((150, 100, 40), 'tilled soil'),
    'C': ((30, 20, 20), 'cave entrance (in a cliff)'),
    'S': ((100, 100, 100), 'stairs up a cliff (2 wide)'),
    'W': ((170, 230, 255), 'waterfall'),
    '_': ((200, 150, 30), 'ledge (jump down south)'),
}
# things on top of the ground
EXTRA = {
    'fence': ((250, 250, 250), 'white fence'),
    'picket': ((200, 200, 255), 'picket fence (Stillbrook only)'),
    'bridge': ((110, 60, 20), 'wooden bridge (north-south, 3 wide)'),
    'bush': ((80, 170, 40), 'round bush'),
    'mailbox': ((255, 0, 0), 'mailbox, 1 wide x 2 tall (Stillbrook only)'),
    'newhouse': ((0, 255, 255), 'new house: Stillbrook/Route 1 5x5, Reedmouth 4x4, Valecrown 4x5, Lanterncross 5x4'),
}
# the house that fits each town's tiles, its size and the room inside
HOUSES = {
    'gTileset_Stillbrook': ('home', 'PalletTown_RivalsHouse_Frlg'),
    'gTileset_VermilionCity': ('verm_house', 'VermilionCity_House1_Frlg'),
    'gTileset_CeladonCity': ('apartment', 'CeladonCity_House1_Frlg'),
    'gTileset_LavenderTown': ('lav_house', 'LavenderTown_House1_Frlg'),
}
FENCE_IDS = {0x0E7, 0x0EC, 0x0ED, 0x0FC, 0x0FD, 0x0F4, 0x0F5}
PICKET_IDS = {0x287, 0x288, 0x290}
BRIDGE_IDS = {0x1C5, 0x1C6, 0x1C7}
BUSH_IDS = {0x005}


def building_colours(n):
    out = []
    for g in (0, 50, 100, 150, 200, 250):
        for b in (60, 120, 180, 240):
            out.append((255, g, b))
    for g in (0, 60, 120, 180, 240):
        for r in (60, 120, 180):
            out.append((r, g, 255))
    assert n <= len(out), 'more buildings than colours'
    return out[:n]


def kind(v):
    m = v & 0x3FF
    for k, ids in (('fence', FENCE_IDS), ('picket', PICKET_IDS), ('bridge', BRIDGE_IDS), ('bush', BUSH_IDS)):
        if m in ids:
            return k
    return None


# ---------------------------------------------------------------- export
def export(c, out):
    os.makedirs(out, exist_ok=True)
    im = Image.new('RGB', (c.w, c.h))
    px = im.load()
    for y in range(c.h):
        for x in range(c.w):
            ch = c.g[y][x]
            px[x, y] = COLOURS.get(ch if ch != 's' else '.', COLOURS['.'])[0]
    for (x, y), v in c.over.items():
        k = kind(v)
        if k and 0 <= x < c.w and 0 <= y < c.h:
            px[x, y] = EXTRA[k][0]
    named = [(n, x, y, i) for n, x, y, i in c.stamps if i and '_NewHouse' not in i]
    for n, x, y, i in c.stamps:
        if i and '_NewHouse' in i:
            for j in range(STAMPS[n].h):
                for k in range(STAMPS[n].w):
                    px[x + k, y + j] = EXTRA['newhouse'][0]
    cols = building_colours(len(named))
    key = {}
    for (n, x, y, i), col in zip(named, cols):
        st = STAMPS[n]
        key['#%02x%02x%02x' % col] = {'building': i, 'stamp': n, 'w': st.w, 'h': st.h}
        for j in range(st.h):
            for k in range(st.w):
                px[x + k, y + j] = col
    for n, x, y, i in c.stamps:
        if n == 'mailbox':
            px[x, y] = px[x, y + 1] = EXTRA['mailbox'][0]
    im.save(os.path.join(out, 'kaldria_south.png'))
    json.dump(key, open(os.path.join(out, 'kaldria_south_key.json'), 'w'), indent=1)
    legend(c, key, out)
    guide(c, im, out)


def legend(c, key, out):
    rows = [(col, name) for col, name in COLOURS.values()] + [(col, name) for col, name in EXTRA.values()]
    rows.append((None, ''))
    rows.append((None, 'BUILDINGS: keep each block its exact size and colour; move it as a whole.'))
    for hexcol, b in key.items():
        col = tuple(int(hexcol[i:i + 2], 16) for i in (1, 3, 5))
        rows.append((col, f"{b['building'].replace('_', ' ')}  ({b['w']}x{b['h']})"))
    im = Image.new('RGB', (520, 24 * len(rows) + 16), 'white')
    d = ImageDraw.Draw(im)
    for i, (col, name) in enumerate(rows):
        y = 8 + i * 24
        if col:
            d.rectangle([8, y, 40, y + 18], fill=col, outline='black')
            d.text((50, y + 4), f'{name}   RGB {col[0]} {col[1]} {col[2]}', fill='black')
        else:
            d.text((8, y + 4), name, fill='black')
    im.save(os.path.join(out, 'colour_key.png'))


def guide(c, im, out, s=6):
    g = im.resize((im.width * s, im.height * s), Image.NEAREST)
    d = ImageDraw.Draw(g)
    for r in c.regions.values():
        d.rectangle([r.x * s, r.y * s, (r.x + r.w) * s - 1, (r.y + r.h) * s - 1], outline=(255, 255, 0), width=2)
        d.text((r.x * s + 6, r.y * s + 6), r.name, fill=(255, 255, 0))
    g.save(os.path.join(out, 'guide_map_edges.png'))


# ---------------------------------------------------------------- import
def nearest(col, table, tol=40):
    best, bd = None, 1e9
    for k, v in table.items():
        dd = sum((a - b) ** 2 for a, b in zip(col, v)) ** 0.5
        if dd < bd:
            best, bd = k, dd
    return best if bd <= tol else None


def load(c):
    """Read the painting (if any) and note where its buildings are, before the towns are laid out."""
    if not os.path.exists(PAINT):
        return None
    im = Image.open(PAINT).convert('RGB')
    assert im.size == (c.w, c.h), f'{PAINT} must stay {c.w}x{c.h} pixels, it is {im.size[0]}x{im.size[1]}'
    key = json.load(open(KEY))
    table = {('g', ch): col for ch, (col, _) in COLOURS.items()}
    table.update({('e', k): col for k, (col, _) in EXTRA.items()})
    for hexcol, b in key.items():
        table[('b', b['building'])] = tuple(int(hexcol[i:i + 2], 16) for i in (1, 3, 5))
    px = im.load()
    cells, bad = {}, []
    for y in range(c.h):
        for x in range(c.w):
            k = nearest(px[x, y], table)
            if k is None:
                bad.append((x, y, px[x, y]))
            cells[(x, y)] = k
    if bad:
        raise SystemExit(f'{len(bad)} pixels have a colour that is not in the key, e.g. ' +
                         ', '.join(f'{x},{y} = {col}' for x, y, col in bad[:6]))
    # buildings: the top-left corner of each block
    found = {}
    for (x, y), k in cells.items():
        if k[0] == 'b':
            fx, fy = found.get(k[1], (x, y))
            found[k[1]] = (min(fx, x), min(fy, y))
    for b in key.values():
        name = b['building']
        if name not in found:
            print(f'paint: {name} is missing from the painting, keeping it where the code puts it')
            continue
        x, y = found[name]
        size = sum(1 for (i, j), k in cells.items() if k == ('b', name))
        if size != b['w'] * b['h'] or any(cells.get((x + i, y + j)) != ('b', name) for i in range(b['w']) for j in range(b['h'])):
            print(f'paint: {name} is not a whole {b["w"]}x{b["h"]} block at {x},{y}; check it')
        c.moved[name] = (x, y)
    # new houses: each block of the shared colour, by its top-left corner
    seen = set()
    c.new_houses = []
    for (x, y), k in sorted(cells.items(), key=lambda p: (p[0][1], p[0][0])):
        if k != ('e', 'newhouse') or (x, y) in seen:
            continue
        todo, block = [(x, y)], set()
        while todo:
            p = todo.pop()
            if p in block or cells.get(p) != ('e', 'newhouse'):
                continue
            block.add(p)
            todo += [(p[0] + 1, p[1]), (p[0] - 1, p[1]), (p[0], p[1] + 1), (p[0], p[1] - 1)]
        seen |= block
        c.new_houses.append((min(p[0] for p in block), min(p[1] for p in block),
                             max(p[0] for p in block) - min(p[0] for p in block) + 1,
                             max(p[1] for p in block) - min(p[1] for p in block) + 1))
    c.painted = True
    return cells


def add_new_houses(c, towns, room):
    """Turn every painted new-house block into a house with a room inside, in whichever map it is."""
    count = {}
    for x, y, w, h in c.new_houses:
        t = next((t for t in towns if t.region.has(x, y)), None)
        if t is None or t.secondary not in HOUSES:
            print(f'paint: the new house at {x},{y} is in a map without houses; skipped')
            continue
        st, tpl = HOUSES[t.secondary]
        if (w, h) != (STAMPS[st].w, STAMPS[st].h):
            print(f'paint: the new house at {x},{y} is {w}x{h}, houses in {t.name} are {STAMPS[st].w}x{STAMPS[st].h}; '
                  'it is placed from its top-left corner')
        count[t.name] = count.get(t.name, 0) + 1
        room(t, st, x, y, f'{t.name}_NewHouse{count[t.name]}', tpl)


def apply(c, cells):
    """Replace the ground drawn by world.py with the painting."""
    for (x, y), k in cells.items():
        c.g[y][x] = k[1] if k[0] == 'g' else '.'
    # fences, pickets, bridges and bushes come from the painting; gym boards and the like stay
    c.over = {p: v for p, v in c.over.items() if not kind(v)}
    has = lambda x, y, e: cells.get((x, y)) == ('e', e)
    for (x, y), k in cells.items():
        if k[0] != 'e':
            continue
        e = k[1]
        if e == 'bush':
            c.over[(x, y)] = blk(0x005, 1, 0)
        elif e == 'picket':
            l, r = has(x - 1, y, e), has(x + 1, y, e)
            c.over[(x, y)] = blk(0x290 if not l else 0x288 if not r else 0x287, 1, 0)
        elif e == 'bridge':
            c.g[y][x] = '~'     # bridges are drawn over water
            l, r = has(x - 1, y, e), has(x + 1, y, e)
            c.over[(x, y)] = blk(0x1C5 if not l else 0x1C7 if not r else 0x1C6, 0, 3)
        elif e == 'fence':
            l, r, u, d = has(x - 1, y, e), has(x + 1, y, e), has(x, y - 1, e), has(x, y + 1, e)
            if d and r and not u:
                m = 0x0EC
            elif d and l and not u:
                m = 0x0ED
            elif u and r and not d:
                m = 0x0FC
            elif u and l and not d:
                m = 0x0FD
            elif u or d:
                # left or right side of a pen: is there more fence to the east on this row?
                m = 0x0F4 if any(has(x + i, y + j, e) for i in range(2, 40) for j in range(-4, 5)) else 0x0F5
            elif not l:
                m = 0x0EC
            elif not r:
                m = 0x0ED
            else:
                m = 0x0E7
            c.over[(x, y)] = blk(m, 1, 0)
        elif e == 'mailbox' and not has(x, y - 1, e):
            c.stamps.append(('mailbox', x, y, None))
    # buildings sit on plain ground
    for n, x, y, i in c.stamps:
        st = STAMPS[n]
        for j in range(st.h):
            for k in range(st.w):
                if c.get(x + k, y + j) in ('T', '^', '~', '≈'):
                    c.set(x + k, y + j, '.')
    for x, y in c.signs:
        c.g[y][x] = 's'


def check_people(c, towns):
    """After painting: people and signs left standing in trees, water, cliffs or buildings."""
    inside = {(x + k, y + j) for n, x, y, _ in c.stamps for j in range(STAMPS[n].h) for k in range(STAMPS[n].w)}
    for t in towns:
        spots = [(o['x'], o['y'], o['graphics_id']) for o in t.objects] + [(b['x'], b['y'], 'sign') for b in t.bgs]
        for x, y, what in spots:
            wx, wy = x + t.ox, y + t.oy
            on_bridge = kind(c.over.get((wx, wy), 0)) == 'bridge'
            if (wx, wy) in inside or (c.g[wy][wx] in 'T^~≈' and not on_bridge and 'SWIMMER' not in what):
                print(f'paint: {t.name}: {what} at {wx},{wy} now stands on {c.g[wy][wx]!r}; move it in world.py')

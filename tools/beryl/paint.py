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
    '^': ((150, 100, 60), 'mountain / cliff, level 1'),
    'M': ((115, 70, 40), 'mountain, level 2 (paint on top of level 1)'),
    'N': ((80, 45, 25), 'mountain, level 3 (paint on top of level 2)'),
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
    'newhouse': ((0, 255, 255), 'new house: Stillbrook/Route 1 5x5, Reedmouth 4x4, Valecrown 7x8, Lanterncross 5x4'),
    'newsmall': ((0, 190, 190), 'new small house: Valecrown 4x5 (elsewhere the same as a new house)'),
    'deco_tall': ((60, 60, 70), 'city building you cannot enter, 5x8 (Valecrown only)'),
    'deco_wide': ((150, 150, 160), 'city building you cannot enter, 7x8 (Valecrown only)'),
}
# what each painted new-building colour turns into: per town tileset, (stamp, inside or None)
DECO = {'deco_tall': 'block_tall', 'deco_wide': 'block_wide'}
# the house that fits each town's tiles, its size and the room inside
HOUSES = {
    'gTileset_Stillbrook': ('home', 'PalletTown_RivalsHouse_Frlg'),
    'gTileset_VermilionCity': ('verm_house', 'VermilionCity_House1_Frlg'),
    'gTileset_CeladonCity': ('condo', 'CeladonCity_House1_Frlg'),
    'gTileset_LavenderTown': ('lav_house', 'LavenderTown_House1_Frlg'),
}
SMALL = {**HOUSES, 'gTileset_CeladonCity': ('apartment', 'CeladonCity_House1_Frlg')}
# someone at home in every new house
RESIDENTS = [
    ('OBJ_EVENT_GFX_WOMAN_1_FRLG', "Oh! A visitor! Sorry about the mess, I wasn't expecting anyone."),
    ('OBJ_EVENT_GFX_OLD_MAN_1', 'In my day we walked everywhere. Bikes! Pah!'),
    ('OBJ_EVENT_GFX_LITTLE_GIRL_FRLG', 'When I grow up I want a POKéMON that can swim up the whole LETHYS!'),
    ('OBJ_EVENT_GFX_MAN', 'The power went out again last night. Third time this month.'),
    ('OBJ_EVENT_GFX_LASS_FRLG', 'Have you been to the park? The POKéMON there come right up to you.'),
    ('OBJ_EVENT_GFX_OLD_WOMAN_FRLG', 'Wipe your feet, dear. ...Well, come in, then.'),
    ('OBJ_EVENT_GFX_YOUNGSTER_FRLG', "My dad says there's something hidden in the old ruins. He won't tell me what."),
    ('OBJ_EVENT_GFX_FAT_MAN_FRLG', "I'd offer you a snack, but I ate them all."),
    ('OBJ_EVENT_GFX_BEAUTY_FRLG', 'They say a strange POKéMON was seen near the dam at night.'),
    ('OBJ_EVENT_GFX_GENTLEMAN_FRLG', 'I collect old maps of KALDRIA. The river used to run somewhere else entirely!'),
]
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
    named = [(n, x, y, i) for n, x, y, i in c.stamps if i and '_New' not in i]
    for n, x, y, i in c.stamps:
        e = 'newhouse' if i and '_NewHouse' in i else 'newsmall' if i and '_NewSmall' in i else \
            next((k for k, v in DECO.items() if v == n and not i), None)
        if e:
            for j in range(STAMPS[n].h):
                for k in range(STAMPS[n].w):
                    px[x + k, y + j] = EXTRA[e][0]
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
    # buildings painted out stay out in the next round too
    json.dump({**key, '_removed': sorted(c.removed)}, open(os.path.join(out, 'kaldria_south_key.json'), 'w'), indent=1)
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
    c.removed |= set(key.pop('_removed', []))
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
    # buildings: the top-left corner of each block; a copied block becomes an extra (new) house
    c.new_houses = []
    for b in key.values():
        name = b['building']
        blocks = components(cells, ('b', name))
        if not blocks:
            print(f'paint: {name} is not in the painting, so it is left out')
            c.removed.add(name)
            continue
        x, y, w, h = blocks[0]
        if (w, h) != (b['w'], b['h']):
            print(f'paint: {name} is {w}x{h} at {x},{y} instead of {b["w"]}x{b["h"]}; check it')
        c.moved[name] = (x, y)
        for extra in blocks[1:]:
            print(f'paint: a copy of {name} at {extra[0]},{extra[1]} becomes a new house')
            c.new_houses.append(('newhouse',) + extra)
    # new houses: each block of the shared colour, by its top-left corner
    for e in ('newhouse', 'newsmall', 'deco_tall', 'deco_wide'):
        c.new_houses += [(e,) + b for b in components(cells, ('e', e))]
    c.painted = True
    return cells


def components(cells, want):
    """(x, y, w, h) of every connected block of cells equal to `want`, top-left first."""
    seen, out = set(), []
    for (x, y), k in sorted(cells.items(), key=lambda p: (p[0][1], p[0][0])):
        if k != want or (x, y) in seen:
            continue
        todo, block = [(x, y)], set()
        while todo:
            p = todo.pop()
            if p in block or cells.get(p) != want:
                continue
            block.add(p)
            todo += [(p[0] + 1, p[1]), (p[0] - 1, p[1]), (p[0], p[1] + 1), (p[0], p[1] - 1)]
        seen |= block
        xs, ys = [p[0] for p in block], [p[1] for p in block]
        out.append((min(xs), min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1))
    return out


def add_new_houses(c, towns, room):
    """Turn every painted new-house block into a house with a room inside, in whichever map it is."""
    count = {}
    for e, x, y, w, h in c.new_houses:
        t = next((t for t in towns if t.region.has(x, y)), None)
        if t is None or t.secondary not in HOUSES or (e in DECO and t.secondary != 'gTileset_CeladonCity'):
            print(f'paint: the {e} at {x},{y} is in a map without that kind of building; skipped')
            continue
        if e in DECO:
            st, tpl = DECO[e], None
        else:
            st, tpl = (SMALL if e == 'newsmall' else HOUSES)[t.secondary]
        if (w, h) != (STAMPS[st].w, STAMPS[st].h):
            print(f'paint: the {e} at {x},{y} is {w}x{h}, it should be {STAMPS[st].w}x{STAMPS[st].h}; '
                  'it is placed from its top-left corner')
        if tpl is None:
            c.building(st, x, y)
            continue
        tag = 'NewSmall' if e == 'newsmall' else 'NewHouse'
        count[(t.name, tag)] = n = count.get((t.name, tag), 0) + 1
        who = RESIDENTS[(sum(map(ord, t.name)) + n * 7 + len(tag)) % len(RESIDENTS)]
        room(t, st, x, y, f'{t.name}_{tag}{n}', tpl, [(who[0], 4, 4, who[1], 'MOVEMENT_TYPE_WANDER_AROUND')])


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
                if c.get(x + k, y + j) in ('T', '^', 'M', 'N', '~', '≈'):
                    c.set(x + k, y + j, '.')
    for x, y in c.signs:
        c.g[y][x] = 's'


def check_people(c, towns):
    """After painting: people and signs left standing in trees, water, cliffs or buildings."""
    inside = {(x + k, y + j) for n, x, y, _ in c.stamps for j in range(STAMPS[n].h) for k in range(STAMPS[n].w)}
    taken = set()
    for t in towns:
        spots = [(o['x'], o['y'], o['graphics_id']) for o in t.objects] + [(b['x'], b['y'], b['type']) for b in t.bgs]
        for x, y, what in spots:
            wx, wy = x + t.ox, y + t.oy
            on_bridge = kind(c.over.get((wx, wy), 0)) == 'bridge'
            if (wx, wy) in inside or (c.g[wy][wx] in 'T^MN~≈' and not on_bridge and 'SWIMMER' not in what):
                nx, ny = free_spot(c, t, wx, wy, inside, taken)
                print(f'paint: {t.name}: {what} at {wx},{wy} was blocked, moved to {nx},{ny}')
                move(c, t, x, y, what, nx, ny)
                taken.add((nx, ny))
            else:
                taken.add((wx, wy))


WALK = '.,*=pb:'


def free_spot(c, t, x, y, inside, taken):
    """The nearest open tile in the same map, not inside or right in front of a building."""
    doors = {(sx + STAMPS[n].door[0], sy + STAMPS[n].door[1] + 1) for n, sx, sy, _ in c.stamps if STAMPS[n].door}
    for r in range(1, 30):
        ring = [(x + dx, y + dy) for dx in range(-r, r + 1) for dy in range(-r, r + 1) if max(abs(dx), abs(dy)) == r]
        ring.sort(key=lambda p: abs(p[0] - x) + abs(p[1] - y))
        for p in ring:
            if t.region.has(*p) and c.g[p[1]][p[0]] in WALK and p not in inside and p not in doors and p not in taken \
                    and (p[0], p[1]) not in c.over:
                return p
    return x, y


def move(c, t, x, y, what, nx, ny):
    lx, ly = nx - t.ox, ny - t.oy
    if what == 'hidden_item':
        b = next(b for b in t.bgs if (b['x'], b['y']) == (x, y))
        b['x'], b['y'] = lx, ly
    elif what == 'sign':
        b = next(b for b in t.bgs if (b['x'], b['y']) == (x, y))
        b['x'], b['y'] = lx, ly
        wx, wy = x + t.ox, y + t.oy
        if c.g[wy][wx] == 's':
            c.g[wy][wx] = '.'
        board = c.over.get((wx, wy - 1), 0) & 0x3FF == 0x160
        if board:   # the red gym board on its post moves along
            post = c.over.pop((wx, wy))
            c.over[(nx, ny - 1)] = c.over.pop((wx, wy - 1))
            c.over[(nx, ny)] = post
        else:
            c.g[ny][nx] = 's'
    else:
        o = next(o for o in t.objects if (o['x'], o['y']) == (x, y))
        o['x'], o['y'] = lx, ly

"""One big drawing of a whole stretch of Kaldria, cut into maps afterwards.

Everything outdoors is drawn into a single Canvas in world coordinates (one character per
metatile, the same legend as mapgen.MapArt). The canvas is turned into metatiles in one go
and then sliced into the maps listed with Canvas.region(), so roads, rivers, cliffs and
forests carry on across map edges by construction.

Two things the Gen 3 engine does are checked here too:
  * a neighbouring map is drawn with the *current* map's tilesets, so tiles from a town's own
    (secondary) tileset must not be visible across an edge to a map that uses another one;
  * only maps that share an edge are drawn, so where nothing is connected the border (trees)
    shows, and the canvas there should be trees as well.
"""
import math
import mapgen
from mapgen import MapArt, STAMPS, NPRI
from kaldria import Grid

# How far past its own edge a map's surroundings are visible (MAP_OFFSET plus one tile of scroll).
VIEW_X, VIEW_Y = 8, 7


class Region:
    def __init__(self, name, x, y, w, h, secondary):
        assert x % 2 == 0 and y % 2 == 0 and w % 2 == 0 and h % 2 == 0, f'{name}: keep regions on even tiles'
        assert (w + 15) * (h + 14) <= 10240, f'{name}: {w}x{h} is too big for the engine'
        self.name, self.x, self.y, self.w, self.h, self.secondary = name, x, y, w, h, secondary

    def has(self, x, y):
        return self.x <= x < self.x + self.w and self.y <= y < self.y + self.h


class Canvas(Grid):
    def __init__(self, w, h, fill='.'):
        super().__init__(w, h, fill)
        self.stamps = []    # (stamp name, x, y, interior or None)
        self.regions = {}
        self.blocks = None
        self.moved = {}      # interior -> (x, y) from a painted map (tools/beryl/paint.py)
        self.signs = []      # sign posts, put back after a painted map replaces the ground
        self.painted = False

    # ---------------------------------------------------------------- drawing
    def get(self, x, y):
        return self.g[y][x] if 0 <= x < self.w and 0 <= y < self.h else None

    def set(self, x, y, ch):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.g[y][x] = ch

    def rect(self, x0, y0, x1, y1, ch, only=None):
        for y in range(max(0, y0), min(self.h, y1 + 1)):
            for x in range(max(0, x0), min(self.w, x1 + 1)):
                if only is None or self.g[y][x] in only:
                    self.g[y][x] = ch
        return self

    def poly(self, pts, ch, only=None):
        """Fill a polygon (cell centres inside it)."""
        ys = [p[1] for p in pts]
        for y in range(max(0, int(min(ys))), min(self.h, int(max(ys)) + 1)):
            cy = y + 0.5
            xs = []
            for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
                if (y0 <= cy < y1) or (y1 <= cy < y0):
                    xs.append(x0 + (cy - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for a, b in zip(xs[::2], xs[1::2]):
                for x in range(max(0, math.ceil(a - 0.5)), min(self.w, math.floor(b - 0.5) + 1)):
                    if only is None or self.g[y][x] in only:
                        self.g[y][x] = ch
        return self

    def band(self, pts, r, ch, only=None):
        """A thick polyline: every cell within r of the line."""
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        for y in range(max(0, int(min(ys) - r - 1)), min(self.h, int(max(ys) + r + 2))):
            for x in range(max(0, int(min(xs) - r - 1)), min(self.w, int(max(xs) + r + 2))):
                px, py = x + 0.5, y + 0.5
                for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
                    dx, dy = x1 - x0, y1 - y0
                    t = 0 if dx == dy == 0 else max(0, min(1, ((px - x0) * dx + (py - y0) * dy) / (dx * dx + dy * dy)))
                    if math.hypot(px - x0 - t * dx, py - y0 - t * dy) <= r:
                        if only is None or self.g[y][x] in only:
                            self.g[y][x] = ch
                        break
        return self

    def road(self, pts, ch='='):
        """A two-wide road through axis-aligned points; each point is the road's top-left tile."""
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            self.rect(min(x0, x1), min(y0, y1), max(x0, x1) + 1, max(y0, y1) + 1, ch)
        return self

    def tidy(self, chars, member=None, rounds=4):
        """Remove one-tile spurs and notches so the autotiler has clean edges to work with.
        chars: the class being cleaned; member: everything that counts as joined to it."""
        member = set(member or chars)
        for _ in range(rounds):
            changed = False
            for y in range(self.h):
                for x in range(self.w):
                    c = self.g[y][x]
                    n = [self.get(x + dx, y + dy) for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0))]
                    inn = [v is None or v in member for v in n]
                    if c in chars:
                        # a lone sliver: open on two opposite sides
                        if (not inn[0] and not inn[1]) or (not inn[2] and not inn[3]):
                            self.g[y][x] = self._around(x, y, member)
                            changed = True
                    elif c in '.,*' and ((inn[0] and inn[1]) or (inn[2] and inn[3])) and sum(inn) >= 3:
                        self.g[y][x] = next(iter(chars))
                        changed = True
            if not changed:
                break
        return self

    def _around(self, x, y, member):
        for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            v = self.get(x + dx, y + dy)
            if v is not None and v not in member:
                return v if v in '.,*=bp:' else '.'
        return '.'

    # ---------------------------------------------------------------- buildings
    def building(self, name, x, y, interior=None):
        """Place a building; returns where it went (a painted map may have moved it)."""
        if self.painted and name == 'mailbox':
            return x, y          # the painting has its own mailboxes
        x, y = self.moved.get(interior, (x, y))
        self.stamps.append((name, x, y, interior))
        st = STAMPS[name]
        # no half trees, rocks or water left under or right around a building
        for j in range(y - 1, y + st.h + 1):
            for i in range(x - 1, x + st.w + 1):
                c = self.get(i, j)
                if c == 'T':
                    cx, cy = i & ~1, j & ~1
                    for a in range(2):
                        for b in range(2):
                            if self.get(cx + a, cy + b) == 'T':
                                self.set(cx + a, cy + b, '.')
                elif c in ('^', '~', '≈') and y <= j < y + st.h and x <= i < x + st.w:
                    self.set(i, j, '.')
        return x, y

    # ---------------------------------------------------------------- maps
    def region(self, name, x, y, w, h, secondary):
        self.regions[name] = Region(name, x, y, w, h, secondary)
        return self.regions[name]

    def build(self):
        art = MapArt('canvas', self.art(), self.stamps, secondary=None)
        art.check_secondary = False
        art.over.update(self.over)
        self.blocks = art.build()
        # each building must sit wholly inside one map that uses its tileset
        for name, x, y, _ in self.stamps:
            st = STAMPS[name]
            owners = {r.name for r in self.regions.values() for j in range(st.h) for i in range(st.w) if r.has(x + i, y + j)}
            assert len(owners) == 1, f'stamp {name} at {x},{y} lies across {owners or "no map"}'
            r = self.regions[owners.pop()]
            need = st.secondary
            if need and need != mapgen.SAME_TILES.get(r.secondary, r.secondary):
                raise ValueError(f'{r.name}: stamp {name} at {x},{y} needs {need}, map uses {r.secondary}')
        return self.blocks

    def slice(self, name):
        r = self.regions[name]
        return [self.blocks[(r.y + j) * self.w + r.x + i] for j in range(r.h) for i in range(r.w)]

    def neighbours(self, r):
        """(direction, other region, offset) for every region sharing an edge with r."""
        out = []
        for o in self.regions.values():
            if o is r:
                continue
            if o.y + o.h == r.y and o.x < r.x + r.w and r.x < o.x + o.w:
                out.append(('up', o, o.x - r.x))
            if r.y + r.h == o.y and o.x < r.x + r.w and r.x < o.x + o.w:
                out.append(('down', o, o.x - r.x))
            if o.x + o.w == r.x and o.y < r.y + r.h and r.y < o.y + o.h:
                out.append(('left', o, o.y - r.y))
            if r.x + r.w == o.x and o.y < r.y + r.h and r.y < o.y + o.h:
                out.append(('right', o, o.y - r.y))
        return out

    def check_edges(self):
        """What each map shows past its edges: wrong-tileset tiles and missing scenery."""
        problems = []
        b = self.blocks
        for r in self.regions.values():
            nb = self.neighbours(r)
            wrong, bare = [], []
            for y in range(r.y - VIEW_Y, r.y + r.h + VIEW_Y):
                for x in range(r.x - VIEW_X, r.x + r.w + VIEW_X):
                    if r.has(x, y):
                        continue
                    src = None
                    for d, o, _ in nb:
                        # a connection shows the neighbour's whole strip beyond that edge
                        if o.has(x, y) and ((d in ('up', 'down') and (y < r.y or y >= r.y + r.h)) or
                                            (d in ('left', 'right') and (x < r.x or x >= r.x + r.w))):
                            src = o
                            break
                    inside = 0 <= x < self.w and 0 <= y < self.h
                    if src is None:
                        if inside and self.g[y][x] != 'T':
                            bare.append((x, y))
                    elif (b[y * self.w + x] & 0x3FF) >= NPRI and src.secondary != r.secondary and \
                            mapgen.SAME_TILES.get(src.secondary, src.secondary) != mapgen.SAME_TILES.get(r.secondary, r.secondary):
                        wrong.append((x, y))
            if wrong:
                problems.append(f'{r.name}: {len(wrong)} tiles of another tileset in view, e.g. {wrong[:4]}')
            if bare:
                problems.append(f'{r.name}: {len(bare)} unconnected tiles that are not trees, e.g. {bare[:4]}')
        return problems


# ---------------------------------------------------------------- maps cut from the canvas
from kaldria import Town  # noqa: E402


class Place(Town):
    """An outdoor map that is one region of the canvas. Everything is given in world coordinates."""

    def __init__(self, canvas, name, x, y, w, h, secondary, **kw):
        super().__init__(name, canvas, secondary=secondary, **kw)
        self.canvas = canvas
        self.region = canvas.region(name, x, y, w, h, secondary)
        self.ox, self.oy = x, y

    def building(self, stamp, x, y, interior=None, dest_warp=0):
        x, y = self.canvas.building(stamp, x, y, interior)
        if interior:
            st = STAMPS[stamp]
            return self.warp(x + st.door[0], y + st.door[1], 'MAP_' + mapgen.upper_id(interior), dest_warp)

    def warp(self, x, y, dest, dest_warp=0, elevation=0):
        assert self.region.has(x, y), f'{self.name}: warp at {x},{y} is outside the map'
        return super().warp(x - self.ox, y - self.oy, dest, dest_warp, elevation)

    def npc(self, gfx, x, y, text=None, **kw):
        assert self.region.has(x, y), f'{self.name}: {gfx} at {x},{y} is outside the map'
        return super().npc(gfx, x - self.ox, y - self.oy, text, **kw)

    def sign(self, x, y, text=None, post=True, **kw):
        assert self.region.has(x, y), f'{self.name}: sign at {x},{y} is outside the map'
        if post and text is not None:
            self.canvas.set(x, y, 's')
            self.canvas.signs.append((x, y))
        return super().sign(x - self.ox, y - self.oy, text, post=False, **kw)

    def add_to(self, proj):
        r = self.region
        self.connections = [{'map': 'MAP_' + mapgen.upper_id(o.name), 'offset': off, 'direction': d}
                            for d, o, off in self.canvas.neighbours(r)]
        lid = proj.add_layout(self.name, r.w, r.h, self.canvas.slice(self.name), mapgen.PRIMARY, self.secondary)
        self.layout_id, self.size = lid, (r.w, r.h)
        proj.add_map({
            'id': self.id, 'name': self.name, 'layout': lid, 'music': self.music, 'region': 'REGION_KANTO',
            'region_map_section': self.mapsec, 'requires_flash': False, 'weather': self.weather,
            'map_type': self.map_type, 'allow_cycling': True, 'allow_escaping': False, 'allow_running': True,
            'show_map_name': self.show_name, 'floor_number': 0, 'battle_scene': 'MAP_BATTLE_SCENE_NORMAL',
            'connections': self.connections or None, 'object_events': self.objects, 'warp_events': self.warps,
            'coord_events': self.coords, 'bg_events': self.bgs,
        }, mapgen.GROUP_OUT, self.scripts())
        for it in self.interiors:
            it.add_to(proj)

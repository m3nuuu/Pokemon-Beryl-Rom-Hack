"""Generates the placeholder art for the first playable test: three painted maps (ground, overlay
and gameplay colour key), the player and NPC sheets and a battle background.

Everything here is a stand-in until Manuel's drawings arrive. The maps are painted per pixel (no
tiles), the same way his drawings will be, so the game code is tested against the real format.

    python3 godot/tools/make_placeholder_art.py
"""
import json
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CELL = 16

BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0

# Gameplay colour key (see docs/DRAWING_GUIDE.md).
KEY = {
    "walk": (255, 255, 255),
    "block": (0, 0, 0),
    "grass": (0, 200, 0),
    "water": (0, 80, 255),
    "ledge": (255, 160, 0),
}


def hexc(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def noise(w, h, scale, seed, octaves=3):
    """Smooth value noise in 0..1."""
    rng = np.random.default_rng(abs(int(seed)))
    acc = np.zeros((h, w))
    amp, total = 1.0, 0.0
    for o in range(octaves):
        s = max(1, int(scale / (2 ** o)))
        gw, gh = w // s + 2, h // s + 2
        grid = (rng.random((gh, gw)) * 255).astype(np.uint8)
        img = Image.fromarray(grid, "L").resize((gw * s, gh * s), Image.BICUBIC)
        acc += np.asarray(img, dtype=float)[:h, :w] / 255.0 * amp
        total += amp
        amp *= 0.5
    acc /= total
    acc = (acc - acc.min()) / (acc.max() - acc.min() + 1e-9)
    return acc


def ramp_pick(value, ramp):
    """Maps 0..1 values onto a colour ramp with ordered dithering (pixel art shading)."""
    h, w = value.shape
    by = np.tile(BAYER, (h // 4 + 1, w // 4 + 1))[:h, :w]
    n = len(ramp)
    idx = np.clip((value * (n - 1) + (by - 0.5) * 0.9).round().astype(int), 0, n - 1)
    pal = np.array([hexc(c) for c in ramp], dtype=np.uint8)
    return pal[idx]


class Canvas:
    def __init__(self, cw, ch, seed):
        self.cw, self.ch = cw, ch
        self.w, self.h = cw * CELL, ch * CELL
        self.ground = np.zeros((self.h, self.w, 4), dtype=np.uint8)
        self.ground[..., 3] = 255
        self.overlay = np.zeros((self.h, self.w, 4), dtype=np.uint8)
        self.key = [["walk"] * cw for _ in range(ch)]
        self.rng = random.Random(seed)
        self.seed = seed

    def paint(self, mask, rgb, layer="ground"):
        arr = self.ground if layer == "ground" else self.overlay
        arr[mask, :3] = rgb[mask] if rgb.ndim == 3 else rgb
        arr[mask, 3] = 255

    def put(self, img, x, y, layer="ground"):
        """Alpha-composite a PIL RGBA image at pixel x, y."""
        arr = self.ground if layer == "ground" else self.overlay
        a = np.asarray(img, dtype=np.uint8)
        h, w = a.shape[:2]
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        sub = a[y0 - y:y1 - y, x0 - x:x1 - x]
        m = sub[..., 3] > 0
        region = arr[y0:y1, x0:x1]
        region[m] = sub[m]

    def set_key(self, cx, cy, kind):
        if 0 <= cx < self.cw and 0 <= cy < self.ch:
            self.key[cy][cx] = kind

    def save(self, name, meta):
        d = os.path.join(ROOT, "maps", name)
        os.makedirs(d, exist_ok=True)
        Image.fromarray(self.ground, "RGBA").convert("RGB").save(os.path.join(d, "ground.png"))
        Image.fromarray(self.overlay, "RGBA").save(os.path.join(d, "overlay.png"))
        key = Image.new("RGB", (self.cw, self.ch))
        for y in range(self.ch):
            for x in range(self.cw):
                key.putpixel((x, y), KEY[self.key[y][x]])
        key.save(os.path.join(d, "gameplay.png"))
        with open(os.path.join(d, "map.json"), "w") as f:
            json.dump(meta, f, indent=2)


# ---------------------------------------------------------------- outdoor materials

GRASS = ["#3f7d34", "#4f9238", "#5fa63f", "#72b84a", "#86c957"]
DIRT = ["#9c7448", "#b08756", "#c39a66", "#d2ad78"]
WATER = ["#2c5d9c", "#3570b4", "#4588c9", "#5aa0da"]
TREE = ["#1f4a2c", "#2b6236", "#3a7a3e", "#4f9446", "#67ad52"]
TALL = ["#2f6a2c", "#3e8435", "#55a043", "#6fbb52"]


def paint_grass(c):
    n = noise(c.w, c.h, 48, c.seed) * 0.7 + noise(c.w, c.h, 10, c.seed + 1) * 0.3
    rgb = ramp_pick(n * 0.75 + 0.15, GRASS)
    c.paint(np.ones((c.h, c.w), bool), rgb)
    # Small blades and highlights so the grass reads as texture, not flat colour.
    for _ in range(c.w * c.h // 60):
        x, y = c.rng.randrange(c.w), c.rng.randrange(1, c.h)
        dark = c.rng.random() < 0.6
        col = hexc(GRASS[0] if dark else GRASS[4])
        c.ground[y, x, :3] = col
        if dark:
            c.ground[y - 1, x, :3] = hexc(GRASS[1])


def path_mask(c, points, width, seed):
    """Soft, hand-drawn looking path along a polyline (points in pixels)."""
    yy, xx = np.mgrid[0:c.h, 0:c.w]
    dist = np.full((c.h, c.w), 1e9)
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        dx, dy = x1 - x0, y1 - y0
        L = dx * dx + dy * dy
        t = np.clip(((xx - x0) * dx + (yy - y0) * dy) / max(L, 1), 0, 1)
        d = np.hypot(xx - (x0 + t * dx), yy - (y0 + t * dy))
        dist = np.minimum(dist, d)
    wob = (noise(c.w, c.h, 14, seed) - 0.5) * 6
    return dist + wob < width, dist + wob < width + 1.5


def paint_dirt(c, mask, rim):
    n = noise(c.w, c.h, 20, c.seed + 5)
    rgb = ramp_pick(n * 0.7 + 0.2, DIRT)
    edge = rim & ~mask
    c.paint(edge, np.array(hexc("#7f6a3c"), dtype=np.uint8))
    c.paint(mask, rgb)
    ys, xs = np.nonzero(mask)
    for i in c.rng.sample(range(len(xs)), min(len(xs), len(xs) // 90)):
        c.ground[ys[i], xs[i], :3] = hexc("#8a6840") if c.rng.random() < 0.5 else hexc("#e2c290")


def paint_water(c, mask_cells_fn):
    """Water body: cells marked by mask_cells_fn(cx, cy), with a sand shore and soft edge."""
    yy, xx = np.mgrid[0:c.h, 0:c.w]
    cellmask = np.zeros((c.h, c.w), bool)
    for cy in range(c.ch):
        for cx in range(c.cw):
            if mask_cells_fn(cx, cy):
                cellmask[cy * CELL:(cy + 1) * CELL, cx * CELL:(cx + 1) * CELL] = True
                c.set_key(cx, cy, "water")
    # Round the corners with a blur, then threshold.
    blur = np.asarray(Image.fromarray((cellmask * 255).astype(np.uint8)).resize(
        (c.w // 16, c.h // 16), Image.BOX).resize((c.w, c.h), Image.BICUBIC), dtype=float) / 255
    wob = (noise(c.w, c.h, 10, c.seed + 9) - 0.5) * 0.25
    water = blur + wob > 0.5
    shore = (blur + wob > 0.32) & ~water
    c.paint(shore, ramp_pick(noise(c.w, c.h, 8, c.seed + 3) * 0.5 + 0.4, DIRT))
    depth = np.clip(blur, 0, 1)
    rgb = ramp_pick(1 - depth * 0.8 + noise(c.w, c.h, 16, c.seed + 4) * 0.25, WATER)
    c.paint(water, rgb)
    edge = water & ~(np.roll(water, 1, 0) & np.roll(water, -1, 0) & np.roll(water, 1, 1) & np.roll(water, -1, 1))
    c.paint(edge, np.array(hexc("#24497a"), dtype=np.uint8))
    ys, xs = np.nonzero(water & (depth > 0.7))
    for i in c.rng.sample(range(len(xs)), min(len(xs), len(xs) // 120)):
        y, x = ys[i], xs[i]
        c.ground[y, x:x + 3, :3] = hexc("#a6d4f2")


def blob(size_w, size_h, seed, ramp, outline="#173a22", light=(-0.6, -0.8), lumps=7):
    """A shaded, lumpy round shape (tree canopy, bush)."""
    rng = random.Random(seed)
    yy, xx = np.mgrid[0:size_h, 0:size_w]
    cx, cy = size_w / 2, size_h / 2
    field = np.zeros((size_h, size_w))
    for i in range(lumps):
        a = i / lumps * math.tau + rng.random() * 0.5
        r = min(size_w, size_h) * 0.28
        px = cx + math.cos(a) * r * 0.75
        py = cy + math.sin(a) * r * 0.7
        rr = r * (0.75 + rng.random() * 0.3)
        field = np.maximum(field, 1 - np.hypot((xx - px) / rr, (yy - py) / rr))
    field = np.maximum(field, 1 - np.hypot((xx - cx) / (size_w * 0.36), (yy - cy) / (size_h * 0.36)))
    inside = field > 0
    # Shading: light from the top left, plus each lump's own roundness.
    nx, ny = (xx - cx) / size_w, (yy - cy) / size_h
    shade = 0.55 - (nx * light[0] + ny * light[1]) * 0.9 + field * 0.5
    shade += (noise(size_w, size_h, 4, seed) - 0.5) * 0.35
    rgb = ramp_pick(np.clip(shade, 0, 1), ramp)
    img = np.zeros((size_h, size_w, 4), np.uint8)
    img[inside, :3] = rgb[inside]
    img[inside, 3] = 255
    edge = inside & ~(np.roll(inside, 1, 0) & np.roll(inside, -1, 0) & np.roll(inside, 1, 1) & np.roll(inside, -1, 1))
    img[edge, :3] = hexc(outline)
    return Image.fromarray(img, "RGBA")


def tree(c, cx, cy, seed):
    """A 2x2-cell tree whose trunk stands on cells (cx, cy) and (cx+1, cy)."""
    x, y = cx * CELL, cy * CELL
    yy, xx = np.mgrid[0:c.h, 0:c.w]
    sx0, sx1, sy0, sy1 = max(0, x - 2), min(c.w, x + 34), max(0, y + 6), min(c.h, y + 18)
    if sx1 > sx0 and sy1 > sy0:
        sub_y, sub_x = yy[sy0:sy1, sx0:sx1], xx[sy0:sy1, sx0:sx1]
        m = ((sub_x - (x + 16)) / 18) ** 2 + ((sub_y - (y + 12)) / 6) ** 2 <= 1
        region = c.ground[sy0:sy1, sx0:sx1, :3]
        region[m] = (region[m] * 0.72).astype(np.uint8)
    trunk = Image.new("RGBA", (12, 14))
    d = ImageDraw.Draw(trunk)
    d.rectangle((2, 0, 9, 13), fill=hexc("#6b4a2e"))
    d.rectangle((2, 0, 3, 13), fill=hexc("#4f3420"))
    d.rectangle((8, 0, 9, 13), fill=hexc("#83603c"))
    d.line((1, 13, 10, 13), fill=hexc("#3e2a18"))
    c.put(trunk, x + 10, y + 1)
    canopy = blob(40, 40, seed, TREE)
    c.put(canopy, x - 4, y - 30)
    c.put(canopy, x - 4, y - 30, "overlay")
    c.set_key(cx, cy, "block")
    c.set_key(cx + 1, cy, "block")


def house(c, cx, cy, w, h, roof, door_dx, wall="#efe3c8"):
    """Building on cells cx..cx+w-1, cy..cy+h-1. The bottom two rows are the front wall, the rest is
    roof. The roof is copied to the overlay so the player walks behind it."""
    x, y, pw, ph = cx * CELL, cy * CELL, w * CELL, h * CELL
    img = Image.new("RGBA", (pw + 8, ph + 18))
    d = ImageDraw.Draw(img)
    ox, oy = 4, 14
    wall_top = oy + ph - 2 * CELL - 4
    # Shadow on the ground to the right and below.
    d.rectangle((ox + 4, oy + ph - 4, ox + pw + 3, oy + ph + 2), fill=(20, 50, 20, 90))
    # Front wall with siding lines.
    d.rectangle((ox, wall_top, ox + pw - 1, oy + ph - 1), fill=hexc(wall))
    for yy in range(wall_top + 4, oy + ph - 1, 4):
        d.line((ox, yy, ox + pw - 1, yy), fill=hexc("#d8c9a8"))
    d.rectangle((ox, oy + ph - 3, ox + pw - 1, oy + ph - 1), fill=hexc("#a08868"))
    d.rectangle((ox, wall_top, ox + pw - 1, oy + ph - 1), outline=hexc("#5b4a36"))
    # Windows.
    for i in range(w):
        if i == door_dx or i % 2 == door_dx % 2:
            continue
        wx = ox + i * CELL + 3
        d.rectangle((wx, wall_top + 7, wx + 9, wall_top + 16), fill=hexc("#8fc6e6"), outline=hexc("#4a5a6a"))
        d.line((wx + 5, wall_top + 7, wx + 5, wall_top + 16), fill=hexc("#4a5a6a"))
        d.line((wx + 1, wall_top + 9, wx + 3, wall_top + 9), fill=(255, 255, 255))
        d.rectangle((wx - 1, wall_top + 17, wx + 10, wall_top + 18), fill=hexc("#6b8a3a"))
    # Door.
    dx = ox + door_dx * CELL + 2
    d.rectangle((dx, oy + ph - 22, dx + 11, oy + ph - 2), fill=hexc("#7a4e2e"), outline=hexc("#3e2716"))
    d.line((dx + 6, oy + ph - 20, dx + 6, oy + ph - 3), fill=hexc("#5e3a20"))
    d.point((dx + 9, oy + ph - 11), fill=hexc("#e8c860"))
    d.rectangle((dx - 1, oy + ph - 1, dx + 12, oy + ph), fill=hexc("#b05040"))
    # Roof with overhang, shaded rows of shingles.
    r = hexc(roof)
    rd = tuple(int(v * 0.72) for v in r)
    rl = tuple(min(255, int(v * 1.18)) for v in r)
    rtop, rbot = oy - 12, wall_top + 2
    rimg = Image.new("RGBA", img.size)
    rdw = ImageDraw.Draw(rimg)
    rdw.polygon([(ox - 4, rbot), (ox + 6, rtop), (ox + pw - 6, rtop), (ox + pw + 3, rbot)], fill=r)
    for yy in range(rtop + 3, rbot, 4):
        rdw.line((ox - 3, yy, ox + pw + 2, yy), fill=rd)
        for xx in range(ox + (yy // 4 % 2) * 4, ox + pw, 8):
            rdw.point((xx, yy - 1), fill=rd)
    rdw.line((ox + 6, rtop, ox + pw - 6, rtop), fill=rl, width=2)
    rdw.line((ox - 4, rbot, ox + pw + 3, rbot), fill=rd, width=2)
    rdw.polygon([(ox - 4, rbot), (ox + 6, rtop), (ox + pw - 6, rtop), (ox + pw + 3, rbot)], outline=hexc("#3a2a2a"))
    # Chimney.
    rdw.rectangle((ox + pw - 20, rtop - 6, ox + pw - 13, rtop + 6), fill=hexc("#8a6a5a"), outline=hexc("#3a2a2a"))
    # Clip the roof to its polygon.
    mask = Image.new("L", img.size)
    ImageDraw.Draw(mask).polygon([(ox - 4, rbot + 1), (ox + 6, rtop - 6), (ox + pw - 6, rtop - 6), (ox + pw + 4, rbot + 1)], fill=255)
    img.paste(rimg, (0, 0), Image.composite(rimg, Image.new("RGBA", img.size), mask))
    c.put(img, x - ox, y - oy)
    roof_only = Image.new("RGBA", img.size)
    roof_only.paste(rimg, (0, 0), rimg)
    c.put(roof_only, x - ox, y - oy, "overlay")
    for yy in range(cy, cy + h):
        for xx in range(cx, cx + w):
            c.set_key(xx, yy, "block")
    c.set_key(cx + door_dx, cy + h - 1, "walk")  # the door itself is a warp you step into
    return (cx + door_dx, cy + h - 1)


def tall_grass(c, cells):
    tuft = Image.new("RGBA", (16, 16))
    d = ImageDraw.Draw(tuft)
    cols = [hexc(t) for t in TALL]
    for bx, h, col in [(1, 9, 1), (4, 12, 2), (7, 10, 1), (10, 13, 3), (13, 9, 2), (3, 7, 0), (9, 7, 0), (12, 6, 1)]:
        d.polygon([(bx, 15), (bx + 1, 15 - h), (bx + 3, 15)], fill=cols[col])
        d.point((bx + 1, 15 - h), fill=cols[3])
    d.line((0, 15, 15, 15), fill=cols[0])
    lower = tuft.crop((0, 8, 16, 16))
    for cx, cy in cells:
        c.put(tuft, cx * CELL, cy * CELL)
        c.put(lower, cx * CELL, cy * CELL + 8, "overlay")
        c.set_key(cx, cy, "grass")


def flowers(c, cx, cy, w, h, colors):
    for _ in range(w * h * 3):
        x = cx * CELL + c.rng.randrange(w * CELL - 3)
        y = cy * CELL + c.rng.randrange(h * CELL - 3)
        col = hexc(c.rng.choice(colors))
        for ddx, ddy in [(1, 0), (0, 1), (2, 1), (1, 2)]:
            c.ground[y + ddy, x + ddx, :3] = col
        c.ground[y + 1, x + 1, :3] = hexc("#fff4a0")


def fence(c, cx, cy, length, horizontal=True):
    for i in range(length):
        x, y = (cx + i, cy) if horizontal else (cx, cy + i)
        img = Image.new("RGBA", (16, 16))
        d = ImageDraw.Draw(img)
        d.rectangle((6, 3, 9, 15), fill=hexc("#c9a070"), outline=hexc("#5e4024"))
        if horizontal:
            d.rectangle((0, 6, 15, 8), fill=hexc("#d8b080"))
            d.line((0, 9, 15, 9), fill=hexc("#5e4024"))
            d.rectangle((6, 3, 9, 15), fill=hexc("#c9a070"), outline=hexc("#5e4024"))
        c.put(img, x * CELL, y * CELL)
        c.set_key(x, y, "block")


def sign(c, cx, cy):
    img = Image.new("RGBA", (16, 16))
    d = ImageDraw.Draw(img)
    d.rectangle((7, 9, 8, 15), fill=hexc("#5e4024"))
    d.rectangle((1, 2, 14, 10), fill=hexc("#c9a070"), outline=hexc("#5e4024"))
    d.line((4, 5, 11, 5), fill=hexc("#7a5a38"))
    d.line((4, 7, 9, 7), fill=hexc("#7a5a38"))
    c.put(img, cx * CELL, cy * CELL)
    c.set_key(cx, cy, "block")


def rock(c, cx, cy, seed):
    img = blob(16, 14, seed, ["#5a5a62", "#74747c", "#90909a", "#ababb4"], outline="#33333a", lumps=4)
    c.put(img, cx * CELL, cy * CELL + 2)
    c.set_key(cx, cy, "block")


def ledge(c, cx, cy, length):
    for i in range(length):
        x, y = (cx + i) * CELL, cy * CELL
        c.ground[y + 9:y + 13, x:x + 16, :3] = hexc("#7a8a4a")
        c.ground[y + 9, x:x + 16, :3] = hexc("#9ab05a")
        c.ground[y + 13:y + 15, x:x + 16, :3] = hexc("#4a5a2a")
        c.set_key(cx + i, cy, "ledge")


# ---------------------------------------------------------------- maps

def make_town():
    c = Canvas(40, 30, 11)
    paint_grass(c)
    P = lambda cx, cy: (cx * CELL + 8, cy * CELL + 8)
    main, rim = path_mask(c, [P(20, -1), P(20, 6), P(18, 12), P(19, 18), P(20, 24), P(20, 30)], 17, 3)
    side, rim2 = path_mask(c, [P(19, 15), P(10, 15), P(9, 13)], 12, 4)
    side2, rim3 = path_mask(c, [P(19, 15), P(29, 14), P(30, 12)], 12, 5)
    paint_dirt(c, main | side | side2, rim | rim2 | rim3)
    flowers(c, 4, 18, 5, 3, ["#f06a8a", "#ffffff", "#f4d040"])
    flowers(c, 24, 4, 4, 2, ["#9a7af0", "#ffffff"])
    paint_water(c, lambda x, y: (x - 9) ** 2 / 12 + (y - 24) ** 2 / 5 <= 1.0)
    # Border of trees, leaving the north exit (x 18..22) open.
    for x in range(-1, 41, 2):
        if not 17 <= x <= 22:
            tree(c, x, 1, x * 7)
        tree(c, x, 30, x * 3 + 1)
    for y in range(3, 30, 2):
        tree(c, -1, y, y * 5)
        tree(c, 39, y, y * 11)
    for x, y in [(2, 3), (4, 5), (35, 3), (34, 26), (26, 26), (14, 27)]:
        tree(c, x, y, x * 13 + y)
    home_door = house(c, 6, 8, 6, 5, "#c0443a", 2)
    lab_door = house(c, 26, 7, 8, 5, "#3a6aa8", 4, wall="#e8ecf0")
    house(c, 13, 19, 5, 4, "#5a8a3a", 1)
    fence(c, 2, 17, 4)
    fence(c, 26, 18, 6)
    sign(c, 12, 13)
    sign(c, 22, 6)
    rock(c, 33, 21, 4)
    rock(c, 4, 26, 6)
    tall_grass(c, [(x, y) for x in range(30, 37) for y in range(21, 25) if not (x == 33 and y == 21)])
    meta = {
        "name": "Test Town",
        "music": "",
        "connections": {"north": {"map": "test_route", "offset": 0}},
        "warps": [
            {"x": home_door[0], "y": home_door[1], "to": "test_house", "to_x": 5, "to_y": 8, "facing": "up"},
            {"x": lab_door[0], "y": lab_door[1], "to": "test_house", "to_x": 5, "to_y": 8, "facing": "up"},
        ],
        "npcs": [
            {"id": "girl", "x": 15, "y": 15, "sprite": "npc_girl", "facing": "down", "wander": True,
             "dialogue": ["Hi! This is the first test of the new STILLBROOK.",
                          "The whole town is one painted picture. No tiles!",
                          "Try the tall grass to the east. Wild POKéMON live there."]},
            {"id": "oldman", "x": 23, "y": 11, "sprite": "npc_oldman", "facing": "left", "wander": False,
             "dialogue": ["The road north leads to ROUTE 1.", "Walk right through, there is no loading screen."]},
        ],
        "signs": [
            {"x": 12, "y": 13, "text": ["BERYL'S HOUSE"]},
            {"x": 22, "y": 6, "text": ["NORTH: ROUTE 1", "SOUTH: work in progress"]},
        ],
        "encounters": {"grass": [
            {"species": "pipwing", "min": 2, "max": 4, "weight": 35},
            {"species": "caddibuzz", "min": 2, "max": 4, "weight": 30},
            {"species": "hivecub", "min": 3, "max": 4, "weight": 20},
            {"species": "pixling", "min": 3, "max": 5, "weight": 15},
        ]},
        "player_start": {"x": 8, "y": 14, "facing": "down"},
    }
    c.save("test_town", meta)


def make_route():
    c = Canvas(40, 44, 23)
    paint_grass(c)
    P = lambda cx, cy: (cx * CELL + 8, cy * CELL + 8)
    m, r = path_mask(c, [P(20, 45), P(20, 38), P(14, 30), P(15, 22), P(24, 14), P(22, 6), P(20, -2)], 16, 8)
    paint_dirt(c, m, r)
    for y in range(-1, 46, 2):
        tree(c, -1, y, y * 5 + 2)
        tree(c, 1, y + 1, y * 3 + 9) if y % 4 == 1 else None
        tree(c, 39, y, y * 7 + 3)
        tree(c, 37, y + 1, y * 9 + 1) if y % 4 == 3 else None
    for x in range(3, 37, 2):
        if not 17 <= x <= 22:
            tree(c, x, 44, x * 7)
            tree(c, x, 1, x * 5 + 3)
    for x, y in [(6, 10), (8, 16), (30, 24), (28, 34), (9, 36), (31, 8), (26, 40)]:
        tree(c, x, y, x * 3 + y * 7)
    tall_grass(c, [(x, y) for x in range(4, 12) for y in range(24, 31)])
    tall_grass(c, [(x, y) for x in range(25, 34) for y in range(15, 21)])
    tall_grass(c, [(x, y) for x in range(23, 32) for y in range(28, 32)])
    tall_grass(c, [(x, y) for x in range(5, 11) for y in range(4, 8)])
    flowers(c, 16, 34, 3, 2, ["#f06a8a", "#ffffff"])
    ledge(c, 26, 11, 9)
    sign(c, 18, 39)
    for x, y in [(12, 20), (34, 38)]:
        rock(c, x, y, x)
    meta = {
        "name": "Route 1 (test)",
        "music": "",
        "connections": {"south": {"map": "test_town", "offset": 0}},
        "warps": [],
        "npcs": [
            {"id": "hiker", "x": 17, "y": 26, "sprite": "npc_hiker", "facing": "right", "wander": True,
             "dialogue": ["Route trainers will battle you here later.", "For now I just like the view."]},
        ],
        "signs": [{"x": 18, "y": 39, "text": ["ROUTE 1 (test)", "The ledge to the north-east can only be jumped down."]}],
        "encounters": {"grass": [
            {"species": "pipwing", "min": 3, "max": 5, "weight": 30},
            {"species": "caddibuzz", "min": 3, "max": 5, "weight": 25},
            {"species": "murkfin", "min": 3, "max": 5, "weight": 10},
            {"species": "geodling", "min": 4, "max": 5, "weight": 15},
            {"species": "wispjel", "min": 4, "max": 6, "weight": 10},
            {"species": "lochlet", "min": 4, "max": 6, "weight": 10},
        ]},
    }
    c.save("test_route", meta)


def make_house():
    c = Canvas(11, 9, 31)
    h, w = c.h, c.w
    # Wooden floor.
    n = noise(w, h, 6, 31)
    floor = ramp_pick(n * 0.5 + 0.3, ["#8a5a34", "#9c6a3e", "#ae7a48", "#c08a54"])
    c.paint(np.ones((h, w), bool), floor)
    for y in range(0, h, 6):
        c.ground[y, :, :3] = hexc("#6e4628")
        off = (y // 6 % 3) * 13
        for x in range(off, w, 40):
            c.ground[y:y + 6, x, :3] = hexc("#6e4628")
    # Back wall (top 2 rows): wallpaper, wainscot.
    c.ground[:30, :, :3] = hexc("#e8d8b8")
    for x in range(0, w, 6):
        c.ground[:22, x, :3] = hexc("#d8c4a0")
    c.ground[22:30, :, :3] = hexc("#a87a50")
    c.ground[22, :, :3] = hexc("#704a2a")
    c.ground[30:32, :, :3] = hexc("#5a3a20")
    for x in range(c.cw):
        c.set_key(x, 0, "block")
        c.set_key(x, 1, "block")

    def furn(cx, cy, cw, ch, draw, block=True):
        img = Image.new("RGBA", (cw * CELL, ch * CELL + 8))
        draw(ImageDraw.Draw(img), img.size)
        c.put(img, cx * CELL, cy * CELL - 8)
        if block:
            for yy in range(cy, cy + ch):
                for xx in range(cx, cx + cw):
                    c.set_key(xx, yy, "block")

    furn(1, 1, 2, 1, lambda d, s: (d.rectangle((2, 2, s[0] - 3, s[1] - 1), fill=hexc("#5a5a6a"), outline=hexc("#202028")),
                                   d.rectangle((5, 5, s[0] - 6, s[1] - 8), fill=hexc("#7ab0d8"))))  # TV
    furn(7, 1, 2, 1, lambda d, s: (d.rectangle((1, 0, s[0] - 2, s[1] - 1), fill=hexc("#8a5a34"), outline=hexc("#3e2716")),
                                   [d.rectangle((3, y, s[0] - 4, y + 3), fill=hexc("#c0a070")) for y in (4, 10, 16)]))  # shelf
    furn(4, 4, 3, 2, lambda d, s: (d.rectangle((1, 6, s[0] - 2, s[1] - 4), fill=hexc("#c08a54"), outline=hexc("#4e3018")),
                                   d.rectangle((1, s[1] - 4, s[0] - 2, s[1] - 1), fill=hexc("#7a4e2e"))))  # table
    furn(9, 3, 1, 2, lambda d, s: (d.rectangle((1, 2, s[0] - 2, s[1] - 2), fill=hexc("#f0f0f8"), outline=hexc("#40405a")),
                                   d.rectangle((1, 2, s[0] - 2, 9), fill=hexc("#d04848")))) # bed
    furn(1, 6, 1, 1, lambda d, s: (d.rectangle((4, 14, 11, 22), fill=hexc("#a05a3a")),
                                   d.ellipse((1, 0, 14, 16), fill=hexc("#3f8a3a"), outline=hexc("#1e4a1e"))))  # plant
    # Door mat (exit).
    c.ground[8 * CELL + 3:8 * CELL + 14, 5 * CELL:6 * CELL, :3] = hexc("#b05040")
    c.ground[8 * CELL + 5:8 * CELL + 12, 5 * CELL + 2:6 * CELL - 2, :3] = hexc("#d07060")
    meta = {
        "name": "House (test)",
        "music": "",
        "indoor": True,
        "connections": {},
        "warps": [{"x": 5, "y": 8, "to": "@return", "exit": "down"}],
        "npcs": [
            {"id": "mom", "x": 2, "y": 4, "sprite": "npc_mom", "facing": "right", "wander": False,
             "dialogue": ["Oh, you're back! Let me heal your POKéMON.", "...", "There. Good as new!"],
             "action": "heal"},
        ],
        "signs": [{"x": 1, "y": 1, "text": ["A show about a river spirit is on.", "Everyone in the region seems to watch it."]}],
        "encounters": {},
    }
    c.save("test_house", meta)


# ---------------------------------------------------------------- characters

def character(path, skin, hair, shirt, pants, hat=None, long_hair=False, beard=None, heavy=False):
    """32x32 frames. Columns: stand, step A, step B. Rows: down, up, left, right."""
    sheet = Image.new("RGBA", (96, 128))
    OUT = (34, 28, 38, 255)
    for row, facing in enumerate(["down", "up", "left", "right"]):
        for col in range(3):
            im = Image.new("RGBA", (32, 32))
            d = ImageDraw.Draw(im)
            bob = 1 if col else 0
            step = [0, 1, -1][col]
            # Shadow.
            d.ellipse((9, 27, 22, 31), fill=(0, 0, 0, 70))
            # Legs.
            lx = [13, 17]
            if facing in ("down", "up"):
                for i, x in enumerate(lx):
                    lift = 1 if (step == 1 and i == 0) or (step == -1 and i == 1) else 0
                    d.rectangle((x, 24 - lift, x + 2, 29 - lift), fill=pants)
                    d.rectangle((x, 29 - lift, x + 2, 29 - lift), fill=OUT)
            else:
                d.rectangle((14 + step * 2, 24, 16 + step * 2, 29), fill=pants)
                d.rectangle((15 - step * 2, 24, 17 - step * 2, 29), fill=tuple(int(v * 0.8) for v in pants))
            # Body.
            bw = 6 if heavy else 5
            d.rounded_rectangle((16 - bw, 16 + bob, 15 + bw, 25 + bob), 2, fill=shirt)
            dark = tuple(int(v * 0.75) for v in shirt)
            d.rectangle((16 - bw, 23 + bob, 15 + bw, 25 + bob), fill=dark)
            # Arms.
            if facing in ("down", "up"):
                sw = step * 1
                d.rectangle((16 - bw - 2, 17 + bob + sw, 16 - bw - 1, 22 + bob + sw), fill=shirt)
                d.rectangle((15 + bw + 1, 17 + bob - sw, 15 + bw + 2, 22 + bob - sw), fill=shirt)
                d.point((16 - bw - 2, 23 + bob + sw), fill=skin)
                d.point((15 + bw + 2, 23 + bob - sw), fill=skin)
            else:
                d.rectangle((15 + step, 18 + bob, 17 + step, 23 + bob), fill=dark)
            # Head.
            d.ellipse((9, 4 + bob, 22, 17 + bob), fill=skin)
            # Hair.
            if facing == "up":
                d.ellipse((9, 3 + bob, 22, 17 + bob), fill=hair)
                if long_hair:
                    d.rectangle((10, 12 + bob, 21, 20 + bob), fill=hair)
            else:
                d.pieslice((8, 3 + bob, 23, 18 + bob), 180, 360, fill=hair)
                if facing == "down":
                    d.rectangle((9, 9 + bob, 11, 12 + bob), fill=hair)
                    d.rectangle((20, 9 + bob, 22, 12 + bob), fill=hair)
                    if long_hair:
                        d.rectangle((8, 9 + bob, 10, 19 + bob), fill=hair)
                        d.rectangle((21, 9 + bob, 23, 19 + bob), fill=hair)
                    d.rectangle((13, 11 + bob, 13, 13 + bob), fill=OUT)
                    d.rectangle((18, 11 + bob, 18, 13 + bob), fill=OUT)
                    if beard:
                        d.rectangle((12, 14 + bob, 19, 17 + bob), fill=beard)
                else:
                    back = 17 if facing == "left" else 9
                    d.rectangle((back, 6 + bob, back + 5, 12 + bob), fill=hair)
                    if long_hair:
                        d.rectangle((back, 9 + bob, back + 5, 19 + bob), fill=hair)
                    ex = 12 if facing == "left" else 19
                    d.rectangle((ex, 11 + bob, ex, 13 + bob), fill=OUT)
                    if beard:
                        bx = 10 if facing == "left" else 16
                        d.rectangle((bx, 14 + bob, bx + 5, 17 + bob), fill=beard)
            if hat:
                d.pieslice((8, 2 + bob, 23, 15 + bob), 180, 360, fill=hat)
                d.rectangle((8, 8 + bob, 23, 9 + bob), fill=hat)
                if facing == "down":
                    d.rectangle((10, 9 + bob, 21, 10 + bob), fill=tuple(int(v * 0.7) for v in hat))
                elif facing == "left":
                    d.rectangle((5, 8 + bob, 12, 10 + bob), fill=tuple(int(v * 0.7) for v in hat))
                elif facing == "right":
                    d.rectangle((19, 8 + bob, 26, 10 + bob), fill=tuple(int(v * 0.7) for v in hat))
            # Outline around the whole figure.
            a = np.asarray(im).copy()
            body = a[..., 3] > 200
            ring = (np.roll(body, 1, 0) | np.roll(body, -1, 0) | np.roll(body, 1, 1) | np.roll(body, -1, 1)) & ~body
            a[ring] = OUT
            sheet.paste(Image.fromarray(a), (col * 32, row * 32))
    sheet.save(path)


def make_characters():
    d = os.path.join(ROOT, "assets", "characters")
    os.makedirs(d, exist_ok=True)
    character(os.path.join(d, "player.png"), (248, 208, 176), (70, 44, 30), (210, 60, 60), (50, 60, 110), hat=(240, 240, 245))
    character(os.path.join(d, "npc_girl.png"), (250, 214, 186), (220, 140, 60), (90, 170, 220), (240, 240, 240), long_hair=True)
    character(os.path.join(d, "npc_oldman.png"), (232, 190, 160), (200, 200, 205), (120, 100, 80), (80, 70, 60), beard=(220, 220, 225))
    character(os.path.join(d, "npc_hiker.png"), (220, 170, 130), (60, 40, 30), (200, 140, 60), (90, 80, 60), hat=(140, 100, 60), heavy=True, beard=(60, 40, 30))
    character(os.path.join(d, "npc_mom.png"), (250, 214, 186), (110, 60, 40), (220, 120, 160), (90, 70, 120), long_hair=True)


# ---------------------------------------------------------------- battle background

def make_battle_bg():
    W, H = 320, 180
    sky = np.linspace(0, 1, 70)[:, None].repeat(W, 1)
    img = np.zeros((H, W, 3), np.uint8)
    img[:70] = ramp_pick(1 - sky * 0.9, ["#8cc4e8", "#a6d4ef", "#c4e4f4", "#e4f2f8"])
    # Clouds.
    cl = noise(W, 70, 24, 77)
    img[:70][cl > 0.68] = hexc("#f4f8fb")
    # Far tree line.
    rng = random.Random(4)
    base = np.zeros(W)
    for x in range(W):
        base[x] = 52 + 6 * math.sin(x / 13) + 4 * math.sin(x / 5.3 + 1) + rng.random() * 2
    yy = np.arange(H)[:, None]
    trees = yy > base[None, :]
    tn = noise(W, H, 6, 5)
    img[trees] = ramp_pick(tn * 0.6 + 0.1, TREE)[trees]
    # Field.
    field = yy > 72 + 0 * base[None, :]
    g = np.linspace(0, 1, H)[:, None].repeat(W, 1)
    img[field] = ramp_pick(np.clip(g * 0.9 + noise(W, H, 20, 6) * 0.25 - 0.15, 0, 1), GRASS)[field]
    out = Image.fromarray(img).convert("RGBA")
    d = ImageDraw.Draw(out)
    # Platforms: enemy (far) and player (near).
    for (cx, cy, rx, ry) in [(236, 82, 54, 12), (82, 160, 74, 17)]:
        d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=hexc("#6f9a44"))
        d.ellipse((cx - rx + 4, cy - ry + 2, cx + rx - 4, cy + ry - 3), fill=hexc("#c39a66"))
        d.ellipse((cx - rx + 10, cy - ry + 4, cx + rx - 10, cy + ry - 6), fill=hexc("#d2ad78"))
    os.makedirs(os.path.join(ROOT, "assets", "battle"), exist_ok=True)
    out.save(os.path.join(ROOT, "assets", "battle", "bg_grass.png"))


if __name__ == "__main__":
    make_town()
    make_route()
    make_house()
    make_characters()
    make_battle_bg()
    print("placeholder art written")

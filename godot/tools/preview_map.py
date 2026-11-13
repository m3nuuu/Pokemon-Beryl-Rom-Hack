"""Draws the gameplay data of a map on top of its picture, so it can be checked without the game.

    python3 godot/tools/preview_map.py test_town [out.png] [--scale 2]

Black = blocked, green = tall grass, blue = water, orange = ledge (jump down only).
Magenta boxes = doors and warps, yellow = signs, cyan = people. Thin lines show the 16px grid.
"""
import json
import os
import sys

from PIL import Image, ImageDraw

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CELL = 16
KEY = {
    "walk": (255, 255, 255), "block": (0, 0, 0), "grass": (0, 200, 0), "water": (0, 80, 255), "ledge": (255, 160, 0),
}
FILL = {"block": (0, 0, 0, 115), "grass": (0, 200, 0, 90), "water": (0, 80, 255, 100), "ledge": (255, 160, 0, 130)}


def nearest(rgba):
    if len(rgba) == 4 and rgba[3] < 128:
        return "walk"
    return min(KEY, key=lambda k: sum((a - b) ** 2 for a, b in zip(rgba[:3], KEY[k])))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    scale = 2
    if "--scale" in sys.argv:
        scale = int(sys.argv[sys.argv.index("--scale") + 1])
        args = [a for a in args if a != str(scale)]
    map_id = args[0]
    out = args[1] if len(args) > 1 else os.path.join(ROOT, "maps", map_id, "preview.png")
    d = os.path.join(ROOT, "maps", map_id)
    img = Image.open(os.path.join(d, "ground.png")).convert("RGBA")
    if os.path.exists(os.path.join(d, "overlay.png")):
        img.alpha_composite(Image.open(os.path.join(d, "overlay.png")).convert("RGBA"))
    w, h = (img.width + CELL - 1) // CELL, (img.height + CELL - 1) // CELL
    key = Image.open(os.path.join(d, "gameplay.png")).convert("RGBA")
    per_cell = key.size == (w, h)
    layer = Image.new("RGBA", img.size)
    dr = ImageDraw.Draw(layer)
    for y in range(h):
        for x in range(w):
            px = (x, y) if per_cell else (min(x * CELL + 8, key.width - 1), min(y * CELL + 8, key.height - 1))
            k = nearest(key.getpixel(px))
            if k in FILL:
                dr.rectangle((x * CELL, y * CELL, x * CELL + CELL - 1, y * CELL + CELL - 1), fill=FILL[k])
    for x in range(w + 1):
        dr.line((x * CELL, 0, x * CELL, img.height), fill=(255, 255, 255, 40))
    for y in range(h + 1):
        dr.line((0, y * CELL, img.width, y * CELL), fill=(255, 255, 255, 40))
    meta = json.load(open(os.path.join(d, "map.json")))
    for group, col in (("warps", (255, 0, 255, 255)), ("signs", (255, 230, 0, 255)), ("npcs", (0, 230, 255, 255))):
        for e in meta.get(group, []):
            x, y = int(e["x"]), int(e["y"])
            dr.rectangle((x * CELL + 1, y * CELL + 1, x * CELL + CELL - 2, y * CELL + CELL - 2), outline=col, width=2)
    img.alpha_composite(layer)
    img = img.resize((img.width * scale, img.height * scale), Image.NEAREST)
    # Cell numbers along the edges, so a spot can be named ("x 12, y 7").
    dr = ImageDraw.Draw(img)
    for x in range(0, w, 5):
        dr.text((x * CELL * scale + 2, 1), str(x), fill=(255, 255, 255))
    for y in range(0, h, 5):
        dr.text((2, y * CELL * scale + 2), str(y), fill=(255, 255, 255))
    img.save(out)
    print("wrote", out)


if __name__ == "__main__":
    main()

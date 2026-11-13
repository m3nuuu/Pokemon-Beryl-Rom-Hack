"""Starts a new map from Manuel's painting.

    python3 godot/tools/new_map.py stillbrook path/to/ground.png [path/to/overlay.png]

Creates godot/maps/<id>/ with the pictures, an all-walkable gameplay.png (one pixel per 16px
cell, ready to paint the colour key on) and a map.json to fill in with doors, people and signs.
"""
import json
import os
import shutil
import sys

from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CELL = 16


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    map_id, ground = sys.argv[1], sys.argv[2]
    overlay = sys.argv[3] if len(sys.argv) > 3 else None
    d = os.path.join(ROOT, "maps", map_id)
    os.makedirs(d, exist_ok=True)
    g = Image.open(ground)
    if g.width % CELL or g.height % CELL:
        print(f"Note: {g.width}x{g.height} is not a multiple of 16. The last row/column of cells is cut off.")
    g.convert("RGB").save(os.path.join(d, "ground.png"))
    if overlay:
        o = Image.open(overlay).convert("RGBA")
        if o.size != g.size:
            sys.exit(f"overlay is {o.size}, ground is {g.size}: they must be the same size")
        o.save(os.path.join(d, "overlay.png"))
    key_path = os.path.join(d, "gameplay.png")
    if not os.path.exists(key_path):
        Image.new("RGB", (g.width // CELL, g.height // CELL), (255, 255, 255)).save(key_path)
    meta_path = os.path.join(d, "map.json")
    if not os.path.exists(meta_path):
        json.dump({
            "name": map_id.replace("_", " ").title(),
            "music": "",
            "connections": {},
            "warps": [],
            "npcs": [],
            "signs": [],
            "encounters": {"grass": []},
        }, open(meta_path, "w"), indent=2)
    print(f"Map {map_id}: {g.width // CELL}x{g.height // CELL} cells in {d}")


if __name__ == "__main__":
    main()

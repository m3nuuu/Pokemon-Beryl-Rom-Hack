"""Render every placed outdoor map into one picture of the region: python3 tools/beryl/worldview.py out.png [scale]"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
import render
import world

lays = render.layouts()
scale = float(sys.argv[2]) if len(sys.argv) > 2 else 0.25
W = max(x + lays['LAYOUT_' + world.upper_id(n)]['width'] for n, (x, y) in world.WORLD.items() if 'LAYOUT_' + world.upper_id(n) in lays)
H = max(y + lays['LAYOUT_' + world.upper_id(n)]['height'] for n, (x, y) in world.WORLD.items() if 'LAYOUT_' + world.upper_id(n) in lays)
im = Image.new('RGB', (W * 16, H * 16), (30, 30, 40))
d = ImageDraw.Draw(im)
for n, (x, y) in world.WORLD.items():
    lid = 'LAYOUT_' + world.upper_id(n)
    if lid not in lays:
        continue
    m = render.render(lays[lid])
    im.paste(m, (x * 16, y * 16))
    d.rectangle([x * 16, y * 16, x * 16 + m.width - 1, y * 16 + m.height - 1], outline=(255, 255, 0))
    d.text((x * 16 + 4, y * 16 + 4), n, fill=(255, 255, 0))
im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS).save(sys.argv[1])

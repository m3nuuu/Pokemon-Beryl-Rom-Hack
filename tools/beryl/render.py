"""Render a map layout (blockdata + tilesets) to a PNG, like Porymap would show it.

    python3 tools/beryl/render.py LAYOUT_ID out.png [--grid]
"""
import json, re, struct, sys, os
from functools import lru_cache
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PRIMARY_METATILES, PRIMARY_TILES, PRIMARY_PALS = 512, 512, 6


@lru_cache(None)
def tileset_dirs():
    out = {}
    src = open(os.path.join(ROOT, 'src/data/tilesets/metatiles.h')).read()
    for name, path in re.findall(r'gMetatiles_(\w+)\[\] = INCBIN_U16\("([^"]+)/metatiles.bin"\)', src):
        out['gTileset_' + name] = os.path.join(ROOT, path)
    return out


def read_pal(path):
    lines = open(path).read().split('\n')[3:19]
    return [tuple(int(v) for v in l.split()[:3]) for l in lines if l.strip()]


@lru_cache(None)
def load_tileset(name):
    d = tileset_dirs()[name]
    img = Image.open(os.path.join(d, 'tiles.png'))
    idx = list(img.get_flattened_data() if hasattr(img, "get_flattened_data") else img.getdata()) if img.mode == 'P' else None
    w = img.width
    tiles = []
    for t in range(img.width // 8 * (img.height // 8)):
        tx, ty = t % (w // 8), t // (w // 8)
        tiles.append([idx[(ty * 8 + y) * w + tx * 8 + x] % 16 for y in range(8) for x in range(8)])
    pals = [read_pal(os.path.join(d, 'palettes', f'{i:02}.pal')) for i in range(16)]
    raw = open(os.path.join(d, 'metatiles.bin'), 'rb').read()
    metas = [struct.unpack_from('<8H', raw, i * 16) for i in range(len(raw) // 16)]
    return tiles, pals, metas


def sizes(primary):
    """Primary tileset size: FRLG primaries hold 640 metatiles and tiles and 7 palettes."""
    return (640, 640, 7) if primary.endswith('Frlg') else (512, 512, 6)


@lru_cache(None)
def metatile_image(primary, secondary, mid):
    ptiles, ppals, pmetas = load_tileset(primary)
    stiles, spals, smetas = load_tileset(secondary)
    PRIMARY_METATILES, PRIMARY_TILES, PRIMARY_PALS = sizes(primary)
    pals = ppals[:PRIMARY_PALS] + spals[PRIMARY_PALS:]
    meta = pmetas[mid] if mid < PRIMARY_METATILES else (smetas[mid - PRIMARY_METATILES] if mid - PRIMARY_METATILES < len(smetas) else None)
    im = Image.new('RGBA', (16, 16), (255, 0, 255, 255))
    if meta is None:
        return im
    px = im.load()
    for layer in range(2):
        for q in range(4):
            v = meta[layer * 4 + q]
            tid, hf, vf, pal = v & 0x3FF, v >> 10 & 1, v >> 11 & 1, v >> 12
            tile = ptiles[tid] if tid < PRIMARY_TILES else (stiles[tid - PRIMARY_TILES] if tid - PRIMARY_TILES < len(stiles) else [0] * 64)
            ox, oy = q % 2 * 8, q // 2 * 8
            for y in range(8):
                for x in range(8):
                    c = tile[(7 - y if vf else y) * 8 + (7 - x if hf else x)]
                    if c == 0 and layer == 1:
                        continue
                    if c == 0 and layer == 0:
                        c = 0
                    px[ox + x, oy + y] = pals[pal][c] + (255,) if pal < len(pals) and c < len(pals[pal]) else (255, 0, 255, 255)
    return im


def layouts():
    return {l['id']: l for l in json.load(open(os.path.join(ROOT, 'data/layouts/layouts.json')))['layouts'] if 'id' in l}


def read_blocks(layout):
    raw = open(os.path.join(ROOT, layout['blockdata_filepath']), 'rb').read()
    return list(struct.unpack(f'<{len(raw) // 2}H', raw))


def render(layout, blocks=None, grid=False, scale=1):
    w, h = layout['width'], layout['height']
    blocks = blocks or read_blocks(layout)
    im = Image.new('RGBA', (w * 16, h * 16))
    for i, b in enumerate(blocks[:w * h]):
        im.paste(metatile_image(layout['primary_tileset'], layout['secondary_tileset'], b & 0x3FF), (i % w * 16, i // w * 16))
    if grid:
        d = ImageDraw.Draw(im)
        for x in range(0, w, 5):
            d.line([(x * 16, 0), (x * 16, h * 16)], fill=(255, 255, 255, 90 if x % 10 else 200))
        for y in range(0, h, 5):
            d.line([(0, y * 16), (w * 16, y * 16)], fill=(255, 255, 255, 90 if y % 10 else 200))
    if scale != 1:
        im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    return im


if __name__ == '__main__':
    lay = layouts()[sys.argv[1]]
    render(lay, grid='--grid' in sys.argv).save(sys.argv[2])

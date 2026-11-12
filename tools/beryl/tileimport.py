"""Add outside metatiles (Emerald, other Kanto towns, Team Aqua's asset repo) to Kaldria's tilesets.

    python3 tools/beryl/tileimport.py

Every Kaldria tileset gets the same imported metatiles at the same ids, starting at IMPORT_BASE, so the
map generator can use them in any town. Each import is drawn from its source, then its 8x8 tiles are
recoloured onto the FireRed primary palettes (or onto a palette slot the tileset has free) and appended
to the tileset's tiles. The tileset's own metatiles and tiles stay as they are: the tool cuts the tileset
back to its original size first, so running it again gives the same result.
"""
import os, struct, sys
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
import render  # noqa: E402

ROOT = render.ROOT
PRIMARY = 'gTileset_General_Frlg'
NPRI_TILES, NPRI_METAS, NPRI_PALS = 640, 640, 7
MAX_SEC_TILES = 1024 - NPRI_TILES
IMPORT_SLOT = 256                      # secondary metatile index of the first import
IMPORT_BASE = NPRI_METAS + IMPORT_SLOT  # its metatile id (0x380)

# Kaldria's outdoor tilesets: directory, original metatile count, original tile count, free palette slot
TILESETS = {
    'gTileset_Stillbrook': ('data/tilesets/secondary/stillbrook', 89, 80, None),
    'gTileset_LavenderTown': ('data/tilesets/secondary/lavender_town_frlg', 218, 256, None),
    'gTileset_VermilionCity': ('data/tilesets/secondary/vermilion_city_frlg', 168, 144, None),
    'gTileset_CeladonCity': ('data/tilesets/secondary/celadon_city_frlg', 240, 256, 7),
}

# FireRed metatile attributes: behaviour (bits 0-8), terrain (9-13), encounter type (24-26), layer (29-30)
LONG_GRASS_ATTR = 0x03 | (1 << 9) | (1 << 24)
NORMAL_ATTR = 0

# name: (source primary, source secondary, source metatile id, attributes, palette to borrow for the free slot)
IMPORTS = [
    ('long_grass', 'gTileset_General', 'gTileset_Fortree', 0x015, LONG_GRASS_ATTR, None),
    ('street', PRIMARY, 'gTileset_SaffronCity', 0x2E9, NORMAL_ATTR, ('gTileset_SaffronCity', 10)),
    ('street_light', PRIMARY, 'gTileset_SaffronCity', 0x2EC, NORMAL_ATTR, ('gTileset_SaffronCity', 10)),
]
IDS = {name: IMPORT_BASE + i for i, (name, *_) in enumerate(IMPORTS)}


def write_pal(path, cols):
    cols = list(cols) + [(0, 0, 0)] * (16 - len(cols))
    open(path, 'w', newline='\r\n').write('JASC-PAL\n0100\n16\n' + ''.join(f'{r} {g} {b}\n' for r, g, b in cols))


def nearest(c, pal):
    """Index 1-15 of the colour in pal closest to c, and the squared error."""
    best, err = 1, 1 << 30
    for i in range(1, 16):
        p = pal[i]
        e = (p[0] - c[0]) ** 2 + (p[1] - c[1]) ** 2 + (p[2] - c[2]) ** 2
        if e < err:
            best, err = i, e
    return best, err


def quantize(px, pals):
    """8x8 RGB pixels -> (palette number, 64 indices) using the palette that fits best."""
    best = None
    for n, pal in pals.items():
        idx, total = [], 0
        for c in px:
            i, e = nearest(c, pal)
            idx.append(i)
            total += e
        if best is None or total < best[0]:
            best = (total, n, idx)
    return best[1], best[2]


def build(name):
    d, nmeta, ntile, free = TILESETS[name]
    d = os.path.join(ROOT, d)
    ppals = render.load_tileset(PRIMARY)[1][:NPRI_PALS]
    spal_paths = [os.path.join(d, 'palettes', f'{i:02}.pal') for i in range(16)]
    spals = [render.read_pal(p) for p in spal_paths]
    pals = {n: ppals[n] for n in range(NPRI_PALS)}
    # the free palette slot takes the colours the imports need, borrowed whole from their source
    borrowed = {src for *_, src in IMPORTS if src}
    assert len(borrowed) <= 1, 'one borrowed palette per tileset for now'
    if free is not None and borrowed:
        src_set, src_pal = borrowed.pop()
        cols = render.load_tileset(src_set)[1][src_pal]
        write_pal(spal_paths[free], cols)
        pals[free] = cols

    img = Image.open(os.path.join(d, 'tiles.png'))
    w = img.width
    flat = list(img.getdata())
    tiles = [[flat[((t // (w // 8)) * 8 + y) * w + (t % (w // 8)) * 8 + x] % 16 for y in range(8) for x in range(8)]
             for t in range(ntile)]
    raw = open(os.path.join(d, 'metatiles.bin'), 'rb').read()[:nmeta * 16]
    attrs = open(os.path.join(d, 'metatile_attributes.bin'), 'rb').read()[:nmeta * 4]
    raw += b'\0' * 16 * (IMPORT_SLOT - nmeta)
    attrs += b'\0' * 4 * (IMPORT_SLOT - nmeta)
    seen = {}
    for iname, sp, ss, mid, attr, borrow in IMPORTS:
        im = render.metatile_image(sp, ss, mid).convert('RGB')
        use = {n: p for n, p in pals.items() if borrow is None or n == free} if (borrow and free is not None) else \
            {n: p for n, p in pals.items() if n < NPRI_PALS}
        entries = []
        for q in range(4):
            ox, oy = q % 2 * 8, q // 2 * 8
            px = [im.getpixel((ox + x, oy + y)) for y in range(8) for x in range(8)]
            pal, idx = quantize(px, use)
            key = tuple(idx)
            if key not in seen:
                seen[key] = len(tiles)
                tiles.append(idx)
            entries.append((NPRI_TILES + seen[key]) | (pal << 12))
        raw += struct.pack('<8H', *entries, 0, 0, 0, 0)
        attrs += struct.pack('<I', attr)
    assert len(tiles) <= MAX_SEC_TILES, f'{name}: {len(tiles)} tiles, the limit is {MAX_SEC_TILES}'
    rows = (len(tiles) + 15) // 16
    out = Image.new('P', (128, rows * 8))
    out.putpalette(img.getpalette())
    data = [0] * (128 * rows * 8)
    for t, tile in enumerate(tiles):
        tx, ty = t % 16, t // 16
        for y in range(8):
            for x in range(8):
                data[(ty * 8 + y) * 128 + tx * 8 + x] = tile[y * 8 + x]
    out.putdata(data)
    out.save(os.path.join(d, 'tiles.png'))
    open(os.path.join(d, 'metatiles.bin'), 'wb').write(raw)
    open(os.path.join(d, 'metatile_attributes.bin'), 'wb').write(attrs)
    return len(tiles) - ntile


if __name__ == '__main__':
    for n in TILESETS:
        print(f'{n}: {len(IMPORTS)} metatiles, {build(n)} new tiles')

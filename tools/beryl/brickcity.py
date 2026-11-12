"""Bring Team Aqua's "Brick City" tileset into the game, for the Valecrown pilot on Emerald's tiles.

    python3 tools/beryl/brickcity.py PATH/TO/Team-Aquas-Asset-Repo-main

Brick City (by Ekat, imported to pokeemerald by Kumatora; see docs/beryl/ASSETS.md) is drawn for
Emerald's General tileset with three layers per metatile. Beryl's engine uses two, so each metatile
keeps the two layers it really uses; the few that use all three get their lower two layers merged
into new tiles. The result is data/tilesets/secondary/brick_city.

It also reads the tileset's example town picture back into metatiles (tools/beryl/brick_city_example.json),
which is where the Brick City buildings and the street edges are cut from.
"""
import json, os, struct, sys
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render  # noqa: E402

ROOT = render.ROOT
OUT = os.path.join(ROOT, 'data/tilesets/secondary/brick_city')
EXAMPLE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'brick_city_example.json')
SRC_REL = 'Tilesets/The Great Tileset Exchange/Full Tilesets/Brick City Secondary'
NPRI = 512
LAYER_NORMAL, LAYER_COVERED = 0, 1


def load_src(repo):
    d = os.path.join(repo, SRC_REL)
    img = Image.open(os.path.join(d, 'tiles.png'))
    w = img.width
    flat = list(img.get_flattened_data())
    tiles = [[flat[((t // (w // 8)) * 8 + y) * w + (t % (w // 8)) * 8 + x] % 16 for y in range(8) for x in range(8)]
             for t in range(w // 8 * (img.height // 8))]
    pals = [render.read_pal(os.path.join(d, 'palettes', f'{i:02}.pal')) for i in range(16)]
    raw = open(os.path.join(d, 'metatiles.bin'), 'rb').read()
    metas = [list(struct.unpack_from('<12H', raw, i * 24)) for i in range(len(raw) // 24)]
    attrs = list(struct.unpack(f'<{len(metas)}H', open(os.path.join(d, 'metatile_attributes.bin'), 'rb').read()))
    return d, img, tiles, pals, metas, attrs


def convert(repo):
    d, img, tiles, pals, metas, attrs = load_src(repo)
    ptiles = render.load_tileset('gTileset_General')[0]
    allpals = pals[:13]

    def tile_px(v):
        tid, hf, vf, pal = v & 0x3FF, v >> 10 & 1, v >> 11 & 1, v >> 12
        t = ptiles[tid] if tid < NPRI else tiles[tid - NPRI]
        return [(t[(7 - y if vf else y) * 8 + (7 - x if hf else x)], pal) for y in range(8) for x in range(8)]

    # tiles that no metatile uses are free for the merged ones
    used = {v & 0x3FF for m in metas for v in m if v & 0x3FF >= NPRI}
    free = [i for i in range(len(tiles)) if i + NPRI not in used]
    out_metas, out_attrs, merged = [], [], 0
    for m, a in zip(metas, attrs):
        layers = [m[0:4], m[4:8], m[8:12]]
        use = [any(v & 0x3FF for v in L) for L in layers]
        lt = LAYER_NORMAL
        if use[0] and use[1] and use[2]:
            # merge bottom and middle into one tile per quarter, recoloured onto the best palette
            low = []
            for q in range(4):
                a_px, b_px = tile_px(layers[0][q]), tile_px(layers[1][q])
                rgb = [allpals[bp][bc] if bc else allpals[ap][ac] for (ac, ap), (bc, bp) in zip(a_px, b_px)]
                best = None
                for pn in range(13):
                    pal = allpals[pn]
                    idx, err = [], 0
                    for c in rgb:
                        k = min(range(1, 16), key=lambda i: sum((pal[i][j] - c[j]) ** 2 for j in range(3)))
                        idx.append(k)
                        err += sum((pal[k][j] - c[j]) ** 2 for j in range(3))
                    if best is None or err < best[0]:
                        best = (err, pn, idx)
                slot = free.pop(0)
                tiles[slot] = best[2]
                low.append((slot + NPRI) | (best[1] << 12))
                merged += 1
            bottom, top = low, layers[2]
        elif use[0] and use[1]:
            bottom, top, lt = layers[0], layers[1], LAYER_COVERED
        elif use[2]:
            bottom, top = (layers[0] if use[0] else layers[1]), layers[2]
        else:
            bottom, top = (layers[0] if use[0] else layers[1]), [0, 0, 0, 0]
        out_metas.append(list(bottom) + list(top))
        out_attrs.append((a & 0x00FF) | (lt << 12))
    os.makedirs(os.path.join(OUT, 'palettes'), exist_ok=True)
    rows = (len(tiles) + 15) // 16
    im = Image.new('P', (128, rows * 8))
    im.putpalette(img.getpalette())
    data = [0] * (128 * rows * 8)
    for t, tile in enumerate(tiles):
        for y in range(8):
            for x in range(8):
                data[(t // 16 * 8 + y) * 128 + t % 16 * 8 + x] = tile[y * 8 + x]
    im.putdata(data)
    im.save(os.path.join(OUT, 'tiles.png'))
    open(os.path.join(OUT, 'metatiles.bin'), 'wb').write(b''.join(struct.pack('<8H', *m) for m in out_metas))
    open(os.path.join(OUT, 'metatile_attributes.bin'), 'wb').write(struct.pack(f'<{len(out_attrs)}H', *out_attrs))
    for i in range(16):
        cols = pals[i] + [(0, 0, 0)] * (16 - len(pals[i]))
        open(os.path.join(OUT, 'palettes', f'{i:02}.pal'), 'w', newline='\r\n').write(
            'JASC-PAL\n0100\n16\n' + ''.join(f'{r} {g} {b}\n' for r, g, b in cols))
    return len(out_metas), merged


def decode_example(repo):
    """Read the example town picture back into metatile ids (Emerald General + Brick City)."""
    import numpy as np
    render.tileset_dirs()['gTileset_BrickCity'] = OUT
    ids = list(range(NPRI)) + [NPRI + i for i in range(os.path.getsize(os.path.join(OUT, 'metatiles.bin')) // 16)]
    imgs = np.stack([np.asarray(render.metatile_image('gTileset_General', 'gTileset_BrickCity', m).convert('RGB'),
                                dtype=np.int16).reshape(-1) for m in ids])
    ex = np.asarray(Image.open(os.path.join(repo, SRC_REL, 'example.png')).convert('RGB'), dtype=np.int16)
    ox, oy = 14, 13  # where the picture's metatile grid starts
    gh, gw = (ex.shape[0] - oy) // 16, (ex.shape[1] - ox) // 16
    grid, err = [], []
    for j in range(gh):
        cells = np.stack([ex[oy + j * 16:oy + j * 16 + 16, ox + i * 16:ox + i * 16 + 16].reshape(-1) for i in range(gw)])
        dist = np.abs(cells[:, None, :] - imgs[None, :, :]).mean(2)
        grid.append([ids[k] for k in dist.argmin(1)])
        err.append([round(float(e), 2) for e in dist.min(1)])
    json.dump({'grid': grid, 'err': err}, open(EXAMPLE, 'w'))
    return gw, gh


if __name__ == '__main__':
    repo = sys.argv[1]
    n, merged = convert(repo)
    print(f'brick_city: {n} metatiles, {merged} merged tiles')
    print('example grid', decode_example(repo))

"""Draw a tileset pair's metatiles with their ids: python3 tools/beryl/sheet.py PRIMARY SECONDARY START COUNT out.png"""
import sys
from PIL import Image, ImageDraw
sys.path.insert(0, __import__('os').path.dirname(__file__))
from render import metatile_image
p, s, start, count, out = sys.argv[1], sys.argv[2], int(sys.argv[3], 0), int(sys.argv[4], 0), sys.argv[5]
cols, sc = 16, 3
im = Image.new('RGB', (cols * 16 * sc, (count + cols - 1) // cols * (16 * sc + 10)), 'white')
d = ImageDraw.Draw(im)
for i in range(count):
    m = metatile_image(p, s, start + i).resize((16 * sc, 16 * sc), Image.NEAREST)
    x, y = i % cols * 16 * sc, i // cols * (16 * sc + 10)
    im.paste(m, (x, y + 10))
    d.text((x + 1, y - 1), f'{start + i:03X}', fill='black')
im.save(out)

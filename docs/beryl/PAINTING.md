# Painting the map

`tools/beryl/kaldria_south.png` is the south of Kaldria with one pixel per tile (212 x 166).
`python3 tools/beryl/world.py` builds every outdoor map from it, cut along the map edges shown in
`guide_map_edges.png`, so the ground always carries on from one map into the next.

* Colours: see `colour_key.png`. Paint with the pencil (hard 1-pixel brush, no anti-aliasing),
  keep the picture 212 x 166, save as PNG.
* Buildings are solid blocks, one colour each. Move a block as a whole and keep its size; its door,
  the warp and its inside move with it. A building must not lie across a map edge.
* New houses: paint a block in the shared new-house colour (RGB 0 255 255), sized for the town: Stillbrook and Route 1 5x5, Reedmouth 4x4, Valecrown 7x8, Lanterncross 5x4. Each becomes a house you can enter.
* Small houses: paint a block in the small-house colour (RGB 0 190 190). In Valecrown that is a 4x5 apartment you can enter; elsewhere it is the town's normal house.
* City buildings you cannot enter (Valecrown only): RGB 60 60 70 for a 5x8 tall block, RGB 150 150 160 for a 7x8 wide block.
* Mailboxes, fences, picket fences, bridges and bushes are painted too.
* People, signs and what happens inside buildings stay in `tools/beryl/world.py`; after a repaint
  the script lists anyone left standing in a tree, a cliff, water or a building.
* `python3 tools/beryl/world.py --export-paint DIR` writes a fresh template, key and guide.
* Fine details can then be done in Porymap; maps changed there must not be regenerated afterwards,
  or the Porymap changes are overwritten.

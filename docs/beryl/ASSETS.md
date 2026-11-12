# Outside assets

## Team Aqua's Asset Repo
Free-to-use Gen 3 decomp assets (tilesets, sprites, music, UI) collected by the Team Aqua's Hideout
community: https://github.com/Pawkkie/Team-Aquas-Asset-Repo. Everything is free to use and edit unless an
asset's own README says otherwise, and each folder's README names who must be credited.

The full repo is 462 MB, so it is not committed here. The zip lives in the project files
(`Team-Aquas-Asset-Repo-main.zip`); unpack it next to this repo when you need it. Only assets we
actually use get copied into the game, each with its credit added to the list below.
Most of its tilesets are in the Emerald format (16-bit metatile attributes, 512-metatile primary), so they
need converting before they work with the FireRed layouts used by Kaldria.

### How outside tiles get into the game
`tools/beryl/tileimport.py` adds metatiles from other tilesets to all four Kaldria outdoor tilesets
(Stillbrook, Lavender, Vermilion, Celadon), at the same ids from 0x380 on. Each import is drawn from its
source, recoloured onto FireRed's primary palettes (or onto a palette slot the tileset has free), and its
tiles are appended. Add an entry to `IMPORTS` and run the script; it rebuilds the tilesets from their
original size each time. The limits are 384 tiles per tileset (Lavender has the least room, about 120
tiles left) and one free palette slot (only Celadon has one).
A Team Aqua tileset is imported the same way once it is registered so the script can draw it.

Imported so far, all from tilesets already in the decomp:
* very tall grass: Emerald's long grass (General tileset, metatile 0x015)
* city street: Saffron City's cobbles (metatiles 0x2E9 and 0x2EC, with Saffron's palette in Celadon's free slot)

### Used in Beryl
(none yet)

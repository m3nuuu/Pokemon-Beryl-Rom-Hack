# Drawing guide

How to draw maps, characters and Pokémon so they drop straight into the game.

## The sizes

| What | Size | Notes |
|---|---|---|
| Game screen | 320 × 180 | Scaled up 6× for 1080p (4× for 720p). |
| Movement grid | 16 × 16 | Invisible. The player moves one cell per step. |
| Overworld character frame | 32 × 32 | About 1 cell wide and 2 cells tall. The feet touch the bottom of the frame. |
| Battle Pokémon (front and back) | 96 × 96 | Transparent PNG. The current 64 × 64 sprites still work. |
| Overworld Pokémon (optional) | 32 × 32 or 64 × 64 | For following Pokémon later. |

Check your scale with the player: a door is about 1 cell wide, a house front is 2 cells tall,
a tree trunk 1 to 2 cells wide.

## Maps: a picture, not tiles

Every town, route and room is **one painted picture**. You can use any brush, shading or detail.
The only rule is the 16 px grid underneath: the width and height must be multiples of 16, and things
the player walks around (walls, trunks, fences, water edges) should roughly follow grid cells.

Each map is a folder with up to four files:

| File | What it is | Who makes it |
|---|---|---|
| `ground.png` | The whole picture, everything included. | You |
| `overlay.png` | Same size, transparent, with only what is drawn **over** the player. | You |
| `gameplay.png` | The colour key: where you can walk, tall grass, water. | You or Claude |
| `map.json` | Doors, people, signs, wild Pokémon, connections to other maps. | Claude |

### What goes on the overlay

Copy these from your picture onto a separate layer and export it as `overlay.png`:

- roofs, and the top part of tall buildings (the player walks behind them)
- tree tops and big bushes
- the lower half of tall grass blades (so they cover the player's feet)
- anything else the player passes under: bridges, arches, signs on poles, lamp tops

Keep its edges hard (no soft, half-transparent edges), or you will see a faint halo.

The easiest way: paint the whole picture in one layer, then duplicate it and erase everything
except roofs and tree tops. Export the first layer as `ground.png` and the second as `overlay.png`.

### The colour key (`gameplay.png`)

Either one pixel per grid cell (a 40 × 30 map gives a 40 × 30 image), or a full-size layer you paint
over the picture. For a full-size layer only the centre of each 16 × 16 cell counts.

| Colour | Hex | Meaning |
|---|---|---|
| White (or transparent) | `#FFFFFF` | walkable |
| Black | `#000000` | blocked |
| Green | `#00C800` | tall grass (walkable, wild Pokémon) |
| Blue | `#0050FF` | water (blocked until Surf) |
| Orange | `#FFA000` | ledge, can only be jumped down (south) |
| Magenta | `#FF00FF` | a door, walkable: tell me where it leads |

You don't have to make the key yourself. Send the picture and I'll mark it and send you a preview
like `godot-preview/test_town_gameplay.png`, with the grid and cell numbers, so you can point at
anything that's wrong ("x 12, y 7 should be blocked").

### Edges between maps

Maps that touch are joined without a loading screen, so the edges have to match: if the road
leaves Stillbrook at cells 18 to 22 on the north edge, Route 1 needs the road at the same cells on
its south edge (or tell me the offset). Trees or cliffs along an edge that has no neighbour keep the
player in; the game also blocks any edge without a connection.

### Rooms

Rooms are drawn the same way, just smaller. Anything outside the room is black, and a room smaller
than the screen is shown in the middle. Mark the door mat; walking down on it leads back outside.

### Small animations

Water, flowers and lamps are separate small sprite sheets placed on the map (frames side by side,
same size each). That part comes in a later step.

## Characters

A sheet is 96 × 128: three columns (standing, step with one foot, step with the other foot) and
four rows (facing down, up, left, right), each frame 32 × 32. See `assets/characters/player.png`.

## Pokémon

Front and back sprites, 96 × 96 PNG with transparency, one file each, named by Pokédex number
(`001.png` in `assets/pokemon/front/`, `001_back.png` in `assets/pokemon/back/`). The battle shows the back sprite in front of the
player; until back sprites exist the front sprite is flipped.

## How to send drawings

Upload the PNGs to the project (or an `.aseprite` / `.kra` file with layers named `ground` and
`overlay`) and say which map it is and which maps it joins. Export at 1× scale, never enlarged.

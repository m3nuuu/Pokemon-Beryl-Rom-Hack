# Kaldria world map (ROM hack)

Built from Manuel's drawing (Nov 2026). One tile = 16 px in game. World coordinates are in tiles,
x to the east, y to the south. Maps that share an edge are connected seamlessly; the generator
(`tools/beryl/world.py`) works the connections out from these positions.

Everything is built on the FireRed/LeafGreen (Kanto) tilesets and is part of the FireRed build
(`make`, which now defaults to `BUILD=firered`; the ROM is `pokefirered.gba`). Each town uses one
Kanto tileset for its buildings: Stillbrook and Route 1 use Pallet Town's (recoloured onto normal
grass as `gTileset_Stillbrook`), Lanterncross and Route 4 Lavender Town's, Reedmouth and the coast
Vermilion City's, Valecrown Celadon City's. Pokémon Centers, marts, gyms and gate houses work anywhere.

Distances are stretched where Manuel asked: the capital sits further from the Lowbank Ruins and
the power station than in the drawing.

## Outdoor maps

| Map | Position | Size | What's there |
|---|---|---|---|
| Victory Road | 0,0 | 40×44 | winding cliff road, Pokémon League at the top |
| Route 9 | 40,8 | 24×36 | mountain path from Frostspring to Emberdeep Cave |
| Frostspring | 64,0 | 72×44 | Ice gym, the Source of the Lethys |
| Mossveil Forest | 136,0 | 36×46 | forest maze |
| Pinehollow | 124,46 | 48×28 | Dragon gym, inside the forest |
| Route 7 | 124,74 | 48×16 | forest path down to Weirhaven |
| Cragmoor | 0,52 | 40×60 | Rock gym, the Mine |
| Route 5 (Lethys Valley) | 40,44 | 64×56 | two roads around the river bend, Cragmoor to Frostspring |
| Mirrormere | 76,100 | 56×30 | the lake behind the dam |
| Weirhaven | 132,90 | 40×30 | Water gym |
| Route 4 | 132,120 | 40×66 | power station, the drop below it, long road to the capital |
| Lethys Dam | 76,130 | 56×20 | the dam crest and spillway |
| Route 2 | 48,120 | 28×30 | stairs from Stillbrook up to the dam |
| Stillbrook | 0,136 | 48×44 | Fighting gym, Beryl's and Jasper's homes |
| Route 3 | 48,150 | 84×36 | river below the dam, Lowbank Ruins, road to the capital |
| Route 1 | 0,180 | 48×74 | Pension and garden, flower fields, farm, windmill |
| Lanterncross | 48,186 | 52×20 | the Lanterncross Temple (the road runs through it), the park and radio tower |
| Reedmouth | 48,206 | 52×36 | Grass gym, harbour, underpass to the capital |
| Valecrown City | 100,186 | 72×60 | capital: Electric gym, shopping centre, casino, bike shop, flower shop, houses |
| Lethys Delta | 48,242 | 52×18 | river mouth, sea |
| Valecrown Beach | 100,246 | 72×14 | beach and sea |

## Caves and buildings you walk through

- Cragway Cave: Stillbrook (north) to Cragmoor (south). "Another Cave" in the drawing; the name is a placeholder.
- Emberdeep Cave: Route 9 to Victory Road.
- The Mine: north of Cragmoor.
- Lanterncross Temple: built into the hillside. The road from Route 3 enters the north gate onto the temple's upper hall (the Ghost gym, Oda), goes down the stairs to the main hall and out of the front doors, then over the bridge to Reedmouth.
- Power Station: Route 4.
- Lethys Dam interior and the maintenance tunnel: under the dam crest.
- Underpass: Reedmouth to Valecrown under the river.

## Kanto data reused

Place names reuse Kanto map sections (renamed): Stillbrook = MAPSEC_PALLET_TOWN, and so on.
Interiors are copies of Kanto rooms (Red's house for Beryl's, the Pokémon Tower for the temple).
The region map picture is still Kanto's until a Kaldria one is drawn.

## Ambience

`WEATHER_LEAVES` is a new weather: a few leaves and petals drifting on the wind (graphics/weather/leaves.png).
Stillbrook and Route 1 use it.

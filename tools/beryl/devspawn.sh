#!/bin/sh
# Build a test ROM (beryl-dev.gba) where a new game starts at MAP X Y instead of Beryl's room.
# usage: tools/beryl/devspawn.sh MAP_STILLBROOK 20 40
set -e
cd "$(dirname "$0")/../.."
cp src/new_game.c /tmp/new_game.c.bak
sed -i "s/MAP_GROUP(MAP_STILLBROOK_BERYLS_HOUSE_2F), MAP_NUM(MAP_STILLBROOK_BERYLS_HOUSE_2F), WARP_ID_NONE, 4, 3)/MAP_GROUP($1), MAP_NUM($1), WARP_ID_NONE, $2, $3)/" src/new_game.c
make -j"$(nproc)" >/dev/null 2>&1 || { cp /tmp/new_game.c.bak src/new_game.c; exit 1; }
cp pokeemerald.gba beryl-dev.gba
cp /tmp/new_game.c.bak src/new_game.c
touch src/new_game.c

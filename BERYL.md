# Pokémon Beryl (ROM hack)

A private Gen 3 fan game built on [pokeemerald-expansion](https://github.com/rh-hideout/pokeemerald-expansion),
set in the region of **Kaldria** along the river **Lethys**. The story canon is in `docs/beryl/GAME_PLAN.md`.

## Build

```
sudo apt install gcc-arm-none-eabi binutils-arm-none-eabi libpng-dev
make -j$(nproc)
```

This produces `pokeemerald.gba`; play it in an emulator such as mGBA. See `INSTALL.md` for Windows/macOS.
Maps are edited with [Porymap](https://github.com/huderlem/porymap).

## Changes from the base

- ROM title `POKEMON BERY`
- Prof. Spruce's intro speech (`data/text/birch_speech.inc`)

Base: pokeemerald-expansion commit c460a8661dfa (31 Oct 2026). This repo is private: it contains Nintendo's code and graphics.

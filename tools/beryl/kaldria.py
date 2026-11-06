"""Helpers for describing Kaldria maps: a char grid you draw into, NPCs, signs,
interiors copied from Hoenn templates, and the script text they need."""
import json, os, textwrap
import mapgen
from mapgen import ROOT, MapArt, Project, STAMPS, upper_id, GROUP_OUT, GROUP_IN, STILLBROOK


# ---------------------------------------------------------------- text
def wrap(text, width=34):
    """Turn plain text into Emerald .string lines: two lines per box."""
    out = []
    for para in text.split('\n\n'):
        lines = textwrap.wrap(para, width)
        for i, l in enumerate(lines):
            if i == len(lines) - 1:
                end = ''
            elif i % 2 == 0:
                end = '\\n'
            else:
                end = '\\p'
            out.append(l + end)
        out[-1] += '\\p'
    out[-1] = out[-1][:-2] + '$'
    return '\n'.join(f'\t.string "{l}"' for l in out)


class Grid:
    def __init__(self, w, h, fill='.'):
        self.w, self.h = w, h
        self.g = [[fill] * w for _ in range(h)]
        self.over = {}  # (x, y) -> exact block value, drawn after everything else

    def fence(self, x0, y0, x1, y1, gaps=()):
        """A white fence around the inclusive rectangle; gaps are (x, y) openings."""
        from mapgen import blk
        for x in range(x0, x1 + 1):
            for y, ch in ((y0, 'top'), (y1, 'bot')):
                m = 0x0E7
                if x == x0:
                    m = 0x0EC if ch == 'top' else 0x0FC
                elif x == x1:
                    m = 0x0ED if ch == 'top' else 0x0FD
                self.over[(x, y)] = blk(m, 1, 0)
        for y in range(y0 + 1, y1):
            self.over[(x0, y)] = blk(0x0F4, 1, 0)
            self.over[(x1, y)] = blk(0x0F5, 1, 0)
        gaps = set(gaps)
        for x, y in gaps:
            self.over.pop((x, y), None)
            self.g[y][x] = '.' if self.g[y][x] in 'T' else self.g[y][x]
        # fence ends either side of a gap
        for x, y in gaps:
            for dx, m in ((-1, 0x0ED), (1, 0x0EC)):
                if (x + dx, y) in self.over and (x + dx, y) not in gaps and y in (y0, y1) and x0 < x + dx < x1:
                    self.over[(x + dx, y)] = blk(m, 1, 0)
        return self

    def hfence(self, x0, x1, y):
        """A straight fence row with rounded ends."""
        from mapgen import blk
        for x in range(x0, x1 + 1):
            self.over[(x, y)] = blk(0x0EC if x == x0 else 0x0ED if x == x1 else 0x0E7, 1, 0)
        return self

    def rect(self, x0, y0, x1, y1, ch):
        """Fill the inclusive rectangle."""
        for y in range(max(0, y0), min(self.h, y1 + 1)):
            for x in range(max(0, x0), min(self.w, x1 + 1)):
                self.g[y][x] = ch
        return self

    def trees(self, x0, y0, x1, y1):
        """Trees on every whole 2x2 cell inside the rectangle."""
        for y in range(y0 + (y0 & 1), y1, 2):
            for x in range(x0 + (x0 & 1), x1, 2):
                if x + 1 <= x1 and y + 1 <= y1:
                    self.rect(x, y, x + 1, y + 1, 'T')
        return self

    def put(self, x, y, s):
        for i, ch in enumerate(s):
            if 0 <= x + i < self.w:
                self.g[y][x + i] = ch
        return self

    def art(self):
        return '\n'.join(''.join(r) for r in self.g)


# ---------------------------------------------------------------- maps
class Town:
    """An outdoor map plus everything inside it."""

    def __init__(self, name, grid, secondary=STILLBROOK, music='MUS_RG_PALLET', mapsec='MAPSEC_PALLET_TOWN',
                 map_type='MAP_TYPE_TOWN', weather='WEATHER_NONE', show_name=True):
        self.name, self.grid = name, grid
        self.id = 'MAP_' + upper_id(name)
        self.secondary, self.music, self.mapsec = secondary, music, mapsec
        self.map_type, self.weather, self.show_name = map_type, weather, show_name
        self.buildings = []   # (stamp, x, y, interior name)
        self.warps = []       # dicts
        self.objects, self.bgs, self.coords = [], [], []
        self.connections = []
        self.script_parts = []
        self.interiors = []
        self.map_scripts = []  # (type, label)

    # building with a door that leads to an interior map
    def building(self, stamp, x, y, interior=None, dest_warp=0):
        self.buildings.append((stamp, x, y, interior))
        if interior:
            st = STAMPS[stamp]
            self.warps.append({'x': x + st.door[0], 'y': y + st.door[1], 'elevation': 0,
                               'dest_map': 'MAP_' + upper_id(interior), 'dest_warp_id': str(dest_warp)})
            return len(self.warps) - 1

    def warp(self, x, y, dest, dest_warp=0, elevation=0):
        self.warps.append({'x': x, 'y': y, 'elevation': elevation, 'dest_map': dest, 'dest_warp_id': str(dest_warp)})
        return len(self.warps) - 1

    def npc(self, gfx, x, y, text=None, move='MOVEMENT_TYPE_FACE_DOWN', rx=0, ry=0, script=None, local=None, flag='0', elevation=3):
        n = len(self.objects) + 1
        label = script or f'{self.name}_EventScript_Npc{n}'
        if text is not None:
            self.script_parts.append(f'{label}::\n\tmsgbox {label}_Text, MSGBOX_NPC\n\tend\n\n{label}_Text:\n{wrap(text)}\n')
        o = {'graphics_id': gfx, 'x': x, 'y': y, 'elevation': elevation, 'movement_type': move,
             'movement_range_x': rx, 'movement_range_y': ry, 'trainer_type': 'TRAINER_TYPE_NONE',
             'trainer_sight_or_berry_tree_id': '0', 'script': label, 'flag': flag}
        if local:
            o = {'local_id': local, **o}
        self.objects.append(o)
        return label

    def sign(self, x, y, text=None, script=None, facing='BG_EVENT_PLAYER_FACING_NORTH', post=True):
        if post and text is not None and self.grid:
            self.grid.put(x, y, 's')
        label = script or f'{self.name}_EventScript_Sign{len(self.bgs) + 1}'
        if text is not None:
            self.script_parts.append(f'{label}::\n\tmsgbox {label}_Text, MSGBOX_SIGN\n\tend\n\n{label}_Text:\n{wrap(text)}\n')
        self.bgs.append({'type': 'sign', 'x': x, 'y': y, 'elevation': 0, 'player_facing_dir': facing, 'script': label})

    def connect(self, direction, other, offset):
        self.connections.append({'map': other if other.startswith('MAP_') else 'MAP_' + upper_id(other),
                                 'offset': offset, 'direction': direction})

    def add_to(self, proj):
        art = MapArt(self.name, self.grid.art(), [(s, x, y, i) for s, x, y, i in self.buildings], secondary=self.secondary)
        art.over.update(self.grid.over)
        blocks = art.build()
        lid = proj.add_layout(self.name, art.w, art.h, blocks, art.primary, art.secondary)
        self.layout_id, self.size = lid, (art.w, art.h)
        proj.add_map({
            'id': self.id, 'name': self.name, 'layout': lid, 'music': self.music, 'region': 'REGION_KANTO',
            'region_map_section': self.mapsec, 'requires_flash': False, 'weather': self.weather,
            'map_type': self.map_type, 'allow_cycling': True, 'allow_escaping': False, 'allow_running': True,
            'show_map_name': self.show_name, 'floor_number': 0, 'battle_scene': 'MAP_BATTLE_SCENE_NORMAL',
            'connections': self.connections or None, 'object_events': self.objects, 'warp_events': self.warps,
            'coord_events': self.coords, 'bg_events': self.bgs,
        }, GROUP_OUT, self.scripts())
        for it in self.interiors:
            it.add_to(proj)

    def scripts(self):
        head = f'{self.name}_MapScripts::\n' + ''.join(f'\tmap_script {t}, {l}\n' for t, l in self.map_scripts) + '\t.byte 0\n\n'
        return head + '\n'.join(self.script_parts)


_TYPES = {}


def map_types():
    """Map id -> map type for every map in the repo."""
    if not _TYPES:
        d = os.path.join(ROOT, 'data/maps')
        for n in os.listdir(d):
            p = os.path.join(d, n, 'map.json')
            if os.path.exists(p):
                m = json.load(open(p))
                _TYPES[m['id']] = m['map_type']
    return _TYPES


def room(town, stamp, x, y, name, template, npcs=(), **kw):
    """A building on `town` whose inside is a copy of `template`; every exit leads back to the door.
    npcs: (gfx, x, y, text[, movement]) tuples."""
    door = town.building(stamp, x, y, name)
    it = Interior(name, template, {'*': (town.name, door)}, **kw)
    for n in npcs:
        gfx, nx, ny, text = n[:4]
        it.npc(gfx, nx, ny, text, move=n[4] if len(n) > 4 else 'MOVEMENT_TYPE_FACE_DOWN')
    town.interiors.append(it)
    return it


class Interior(Town):
    """A room copied from a Hoenn map: same layout and warp spots, our own people."""

    def __init__(self, name, template, links, music=None, mapsec=None, keep_bgs=False):
        t = json.load(open(os.path.join(ROOT, 'data/maps', template, 'map.json')))
        super().__init__(name, None, music=music or t['music'], mapsec=mapsec or t['region_map_section'],
                         map_type=t['map_type'], weather=t['weather'], show_name=False)
        self.template = t
        self.layout_id = t['layout']
        # links: template dest map (or (map, warp id)) -> (our map name, dest warp id or None to keep).
        # '*' catches every warp that leads outdoors; anything still unmatched is dropped.
        for w in t['warp_events']:
            key = (w['dest_map'], str(w['dest_warp_id']))
            if key in links or w['dest_map'] in links:
                dest, wid = links.get(key, links.get(w['dest_map']))
            elif '*' in links and map_types().get(w['dest_map']) not in ('MAP_TYPE_INDOOR', 'MAP_TYPE_UNDERGROUND'):
                dest, wid = links['*']
            else:
                continue
            self.warps.append({**w, 'dest_map': 'MAP_' + upper_id(dest) if not dest.startswith('MAP_') else dest,
                               'dest_warp_id': str(w['dest_warp_id'] if wid is None else wid)})
        if keep_bgs:
            self.bgs = [b for b in t['bg_events']]

    def add_to(self, proj):
        t = self.template
        proj.add_map({
            'id': self.id, 'name': self.name, 'layout': self.layout_id, 'music': self.music, 'region': t['region'],
            'region_map_section': self.mapsec, 'requires_flash': False, 'weather': self.weather,
            'map_type': self.map_type, 'allow_cycling': False, 'allow_escaping': False, 'allow_running': False,
            'show_map_name': False, 'floor_number': t.get('floor_number', 0), 'battle_scene': 'MAP_BATTLE_SCENE_NORMAL', 'connections': None,
            'object_events': self.objects, 'warp_events': self.warps, 'coord_events': self.coords, 'bg_events': self.bgs,
        }, GROUP_IN, self.scripts())


def pokecenter(town, x, y, heal_id, proj_heals):
    """A Pokémon Center building, its inside, nurse and heal location."""
    inside = f'{town.name}_PokemonCenter_1F'
    door = town.building('pokecenter', x, y, inside)
    it = Interior(inside, 'ViridianCity_PokemonCenter_1F_Frlg',
                  {'MAP_VIRIDIAN_CITY': (town.name, door), 'MAP_VIRIDIAN_CITY_POKEMON_CENTER_2F': (town.name, door)})
    # the stairs to the 2F have nowhere to go yet
    it.warps = [w for w in it.warps if w['y'] == 8]
    local = f'LOCALID_{upper_id(town.name)}_NURSE'
    it.map_scripts.append(('MAP_SCRIPT_ON_TRANSITION', f'{inside}_OnTransition'))
    it.map_scripts.append(('MAP_SCRIPT_ON_RESUME', 'CableClub_OnResume'))
    it.script_parts.append(f'{inside}_OnTransition:\n\tsetrespawn {heal_id}\n\tend\n\n'
                           f'{inside}_EventScript_Nurse::\n\tlock\n\tfaceplayer\n\tcall EventScript_PkmnCenterNurse_Frlg\n'
                           f'\trelease\n\tend\n')
    it.npc('OBJ_EVENT_GFX_NURSE_FRLG', 7, 2, script=f'{inside}_EventScript_Nurse', local=local)
    town.interiors.append(it)
    st = STAMPS['pokecenter']
    # the P.C sign on the front works by itself (metatile behaviour)
    proj_heals.append({'id': heal_id, 'map': town.id, 'x': x + st.door[0], 'y': y + st.door[1] + 1,
                       'respawn_map': it.id, 'respawn_npc': local})
    return it


def mart(town, x, y, items):
    inside = f'{town.name}_Mart'
    door = town.building('mart', x, y, inside)
    it = Interior(inside, 'ViridianCity_Mart_Frlg', {'MAP_VIRIDIAN_CITY': (town.name, door)})
    lab = f'{inside}_EventScript_Clerk'
    it.script_parts.append(f'{lab}::\n\tlock\n\tfaceplayer\n\tmessage gText_HowMayIServeYou\n\twaitmessage\n'
                           f'\tpokemart {inside}_Items\n\tmsgbox gText_PleaseComeAgain, MSGBOX_DEFAULT\n\trelease\n\tend\n\n'
                           f'\t.align 2\n{inside}_Items:\n' + ''.join(f'\t.2byte {i}\n' for i in items) + '\tpokemartlistend\n')
    it.npc('OBJ_EVENT_GFX_CLERK', 2, 3, script=lab, move='MOVEMENT_TYPE_FACE_RIGHT')
    town.interiors.append(it)
    return it

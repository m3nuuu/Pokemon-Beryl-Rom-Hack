"""Helpers for describing Kaldria maps: a char grid you draw into, NPCs, signs,
interiors copied from Hoenn templates, and the script text they need."""
import json, os, textwrap
import mapgen
from mapgen import ROOT, MapArt, Project, STAMPS, upper_id, GROUP_OUT, GROUP_IN


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
                m = 0x149
                if x == x0:
                    m = 0x138 if ch == 'top' else 0x148
                elif x == x1:
                    m = 0x13A if ch == 'top' else 0x14A
                self.over[(x, y)] = blk(m, 1, 0)
        for y in range(y0 + 1, y1):
            self.over[(x0, y)] = blk(0x140, 1, 0)
            self.over[(x1, y)] = blk(0x142, 1, 0)
        for x, y in gaps:
            self.over.pop((x, y), None)
            self.g[y][x] = '.' if self.g[y][x] in 'T' else self.g[y][x]
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

    def __init__(self, name, grid, secondary='gTileset_Petalburg', music='MUS_LITTLEROOT', mapsec='MAPSEC_LITTLEROOT_TOWN',
                 map_type='MAP_TYPE_TOWN', weather='WEATHER_SUNNY', show_name=True):
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
    def building(self, stamp, x, y, interior=None):
        self.buildings.append((stamp, x, y, interior))
        if interior:
            st = STAMPS[stamp]
            self.warps.append({'x': x + st.door[0], 'y': y + st.door[1], 'elevation': 0,
                               'dest_map': 'MAP_' + upper_id(interior), 'dest_warp_id': '0'})
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
            'id': self.id, 'name': self.name, 'layout': lid, 'music': self.music, 'region': 'REGION_HOENN',
            'region_map_section': self.mapsec, 'requires_flash': False, 'weather': self.weather,
            'map_type': self.map_type, 'allow_cycling': True, 'allow_escaping': False, 'allow_running': True,
            'show_map_name': self.show_name, 'battle_scene': 'MAP_BATTLE_SCENE_NORMAL',
            'connections': self.connections or None, 'object_events': self.objects, 'warp_events': self.warps,
            'coord_events': self.coords, 'bg_events': self.bgs,
        }, GROUP_OUT, self.scripts())
        for it in self.interiors:
            it.add_to(proj)

    def scripts(self):
        head = f'{self.name}_MapScripts::\n' + ''.join(f'\tmap_script {t}, {l}\n' for t, l in self.map_scripts) + '\t.byte 0\n\n'
        return head + '\n'.join(self.script_parts)


class Interior(Town):
    """A room copied from a Hoenn map: same layout and warp spots, our own people."""

    def __init__(self, name, template, links, music=None, mapsec=None, keep_bgs=False):
        t = json.load(open(os.path.join(ROOT, 'data/maps', template, 'map.json')))
        super().__init__(name, None, music=music or t['music'], mapsec=mapsec or t['region_map_section'],
                         map_type=t['map_type'], weather=t['weather'], show_name=False)
        self.template = t
        self.layout_id = t['layout']
        # links: template dest map -> (our map name, dest warp id or None to keep)
        for w in t['warp_events']:
            dest, wid = links.get(w['dest_map'], (None, None))
            if dest is None:
                raise ValueError(f'{name}: no link for warp to {w["dest_map"]}')
            self.warps.append({**w, 'dest_map': 'MAP_' + upper_id(dest) if not dest.startswith('MAP_') else dest,
                               'dest_warp_id': str(w['dest_warp_id'] if wid is None else wid)})
        if keep_bgs:
            self.bgs = [b for b in t['bg_events']]

    def add_to(self, proj):
        t = self.template
        proj.add_map({
            'id': self.id, 'name': self.name, 'layout': self.layout_id, 'music': self.music, 'region': 'REGION_HOENN',
            'region_map_section': self.mapsec, 'requires_flash': False, 'weather': self.weather,
            'map_type': self.map_type, 'allow_cycling': False, 'allow_escaping': False, 'allow_running': False,
            'show_map_name': False, 'battle_scene': 'MAP_BATTLE_SCENE_NORMAL', 'connections': None,
            'object_events': self.objects, 'warp_events': self.warps, 'coord_events': self.coords, 'bg_events': self.bgs,
        }, GROUP_IN, self.scripts())


def pokecenter(town, x, y, heal_id, proj_heals):
    """A Pokémon Center building, its inside, nurse and heal location."""
    inside = f'{town.name}_PokemonCenter_1F'
    door = town.building('pokecenter', x, y, inside)
    it = Interior(inside, 'PetalburgCity_PokemonCenter_1F',
                  {'MAP_PETALBURG_CITY': (town.name, door), 'MAP_PETALBURG_CITY_POKEMON_CENTER_2F': (town.name, door)})
    # stairs to the 2F have nowhere to go yet; send them out of the door
    it.warps = it.warps[:2]
    local = f'LOCALID_{upper_id(town.name)}_NURSE'
    it.map_scripts.append(('MAP_SCRIPT_ON_TRANSITION', f'{inside}_OnTransition'))
    it.map_scripts.append(('MAP_SCRIPT_ON_RESUME', 'CableClub_OnResume'))
    it.script_parts.append(f'{inside}_OnTransition:\n\tsetrespawn {heal_id}\n\tend\n\n'
                           f'{inside}_EventScript_Nurse::\n\tsetvar VAR_0x800B, {local}\n\tcall Common_EventScript_PkmnCenterNurse\n'
                           f'\twaitmessage\n\twaitbuttonpress\n\trelease\n\tend\n')
    it.npc('OBJ_EVENT_GFX_NURSE', 7, 2, script=f'{inside}_EventScript_Nurse', local=local)
    town.interiors.append(it)
    st = STAMPS['pokecenter']
    town.sign(x + st.door[0] + 1, y + st.door[1], script='Common_EventScript_ShowPokemonCenterSign')
    proj_heals.append({'id': heal_id, 'map': town.id, 'x': x + st.door[0], 'y': y + st.door[1] + 1,
                       'respawn_map': it.id, 'respawn_npc': local})
    return it


def mart(town, x, y, items):
    inside = f'{town.name}_Mart'
    door = town.building('mart', x, y, inside)
    it = Interior(inside, 'PetalburgCity_Mart', {'MAP_PETALBURG_CITY': (town.name, door)})
    lab = f'{inside}_EventScript_Clerk'
    it.script_parts.append(f'{lab}::\n\tlock\n\tfaceplayer\n\tmessage gText_HowMayIServeYou\n\twaitmessage\n'
                           f'\tpokemart {inside}_Items\n\tmsgbox gText_PleaseComeAgain, MSGBOX_DEFAULT\n\trelease\n\tend\n\n'
                           f'\t.align 2\n{inside}_Items:\n' + ''.join(f'\t.2byte {i}\n' for i in items) + '\tpokemartlistend\n')
    it.npc('OBJ_EVENT_GFX_MART_EMPLOYEE', 1, 3, script=lab, move='MOVEMENT_TYPE_FACE_RIGHT')
    town.interiors.append(it)
    st = STAMPS['mart']
    town.sign(x + st.door[0] + 1, y + st.door[1], script='Common_EventScript_ShowPokemartSign')
    return it

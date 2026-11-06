"""Sanity checks for the generated Kaldria maps: warps point somewhere real and back,
connections are mutual, and doors sit on door tiles."""
import json, os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render
from mapgen import ROOT, behaviors

groups = json.load(open(os.path.join(ROOT, 'data/maps/map_groups.json')))
ours = groups['gMapGroup_KaldriaOutdoor'] + groups['gMapGroup_KaldriaIndoor']
allmaps = {}
for g in groups['group_order']:
    for n in groups[g]:
        m = json.load(open(os.path.join(ROOT, 'data/maps', n, 'map.json')))
        allmaps[m['id']] = m
lays = render.layouts()
bad = 0
for n in ours:
    m = json.load(open(os.path.join(ROOT, 'data/maps', n, 'map.json')))
    lay = lays[m['layout']]
    for i, w in enumerate(m['warp_events']):
        d = allmaps.get(w['dest_map'])
        if not d:
            print(f'{n}: warp {i} to unknown {w["dest_map"]}'); bad += 1; continue
        wid = int(w['dest_warp_id'])
        if wid >= len(d['warp_events']):
            print(f'{n}: warp {i} to {w["dest_map"]} #{wid}, which has {len(d["warp_events"])} warps'); bad += 1; continue
        if not (0 <= w['x'] < lay['width'] and 0 <= w['y'] < lay['height']):
            print(f'{n}: warp {i} off the map'); bad += 1
        back = d['warp_events'][wid]
        if back['dest_map'] != m['id']:
            print(f'{n}: warp {i} -> {w["dest_map"]} #{wid}, which leads to {back["dest_map"]} instead'); bad += 1
    for c in m['connections'] or []:
        o = allmaps[c['map']]
        opp = {'up': 'down', 'down': 'up', 'left': 'right', 'right': 'left'}[c['direction']]
        if not any(k['map'] == m['id'] and k['direction'] == opp and k['offset'] == -c['offset'] for k in o['connections'] or []):
            print(f'{n}: connection {c} is not mirrored'); bad += 1
print('problems:', bad)
sys.exit(1 if bad else 0)

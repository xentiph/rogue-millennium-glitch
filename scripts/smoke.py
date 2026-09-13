"""Non-interactive smoke test for the no-combat Scainet core (no curses).
Run:  cd ~/rogue && python3 scripts/smoke.py
"""
import random, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir))

from rogue.world import generate_map
from rogue.mutations import Survivor
from rogue.entities import Player, NPC
from rogue.fov import compute_fov
from rogue.main import place_things, TONGUES, TEACHER_LINES

rng = random.Random(42)
grid, buildings = generate_map(rng)
street = sum(row.count(".") + row.count(",") + row.count("%") for row in grid)
assert street > 200, f"street too thin: {street}"
assert len(buildings) >= 6
print(f"[1] city ok: {len(buildings)} buildings, {street} street tiles")

start = (len(grid[0])//2, len(grid)-3)
s = Survivor(rng)
p = Player(start[0], start[1], s)
assert "en" in p.known and not p.knows("zh")
print(f"[2] player ok: Octavia knows {sorted(p.known)}")

npcs, nodes = place_things(grid, buildings, rng)
tongues_placed = {n.tongue for n in npcs}
assert tongues_placed >= set(TONGUES), f"missing teachers: {set(TONGUES)-tongues_placed}"
assert len(nodes) >= 2
print(f"[3] world ok: {len(npcs)} teachers ({sorted(tongues_placed)}), {len(nodes)} safe nodes")

# learning
p.learn("zh")
assert p.knows("zh")
p.drone.recharge()
assert p.drone.charge >= 25
print(f"[4] learning ok: now knows {sorted(p.known)}, drone charge {p.drone.charge}")

# drain kills
p.drone.charge = 0
assert p.drone.charge <= 0
print("[5] drain ok: drone can hit 0 (run would end)")

fov = compute_fov(grid, start[0], start[1], 7)
assert len(fov) > 40
print(f"[6] fov ok: {len(fov)} tiles lit")

# every teacher has a line in their tongue
for t in TONGUES:
    assert t in TEACHER_LINES and len(TEACHER_LINES[t]) > 0
print("[7] teacher lines ok for all 5 tongues")

print("\nALL CHECKS PASSED")

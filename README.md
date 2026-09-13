# Rogue: The Millenium Glitch

An ASCII roguelike built for the terminal. Stdlib only (Python 3 + curses).

**You are Octavia** — trans Black, homeless in New York. You wake at dawn,
blacked out, as two cops pull your tent off the sidewalk and drive east with
it. The world renders you as a black `@` on the lighter tiles of the street,
because you never see yourself in a mirror in ASCII-land.

The Matrix-green oracle surfaces at midnight. Cross the ocean. The dream
doesn't end in Shanghai — it ends in **Nanjing**, green and brown solarpunk.

## Run
```
cd ~/rogue && python3 -m rogue.main
```
Move: `h j k l` / arrows · Shove: `a` · Wait: `.` · Quit: `q`

## Smoke test
```
cd ~/rogue && python3 scripts/smoke.py
```

## Modules
- `rogue/main.py` — game loop (NY → Nanjing; ScaiNet at midnight)
- `rogue/world.py` — procedural New York street block (buildings, doors, puddles, trash, parks)
- `rogue/mutations.py` — survivor origins
- `rogue/entities.py` — Octavia, street threats, turn-based combat
- `rogue/fov.py` — shadow-cast field of view
- `rogue/scai.py` — the ScaiNet oracle (matrix green)

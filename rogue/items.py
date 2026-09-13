"""Items for Scainet — body & sanity.
Every soul starts having LOST their boccea (the bundled belongings they
carried). Until they find a new one, they have no way to carry things —
they can only grab and use something in the immediate moment.

Items restore two needs:
  - BODY  -> restores warmth (the body's resource)
  - SANITY-> restores the mind (and can hold a tongue)

The boccea itself is a special item: it is the container. Finding one lets
the soul hoard and ration instead of consuming on the spot.
"""
import random

# item: glyph, name, kind ('body'/'sanity'), effect dict, flavor
ITEMS = {
    "f": dict(name="crust of bread", kind="body", warmth=20, san=0,
              pick="You eat the stale bread. Some warmth returns."),
    "w": dict(name="clean water", kind="body", warmth=0, san=12,
              pick="You drink. Thirst lets go of the mind."),
    "C": dict(name="a heavy coat", kind="body", warmth=30, san=0,
              pick="You pull the coat on. The cold stops biting as hard."),
    "n": dict(name="a rough blanket", kind="body", warmth=15, san=0,
              pick="You wrap the blanket close. You can breathe again."),
    "K": dict(name="medicine", kind="san", warmth=0, san=25,
              pick="The medicine steadies the shaking in your hands."),
    "p": dict(name="a photograph", kind="san", warmth=0, san=20,
              pick="A face you almost lost. Your heart remembers why."),
    "l": dict(name="a letter", kind="san", warmth=0, san=18,
              pick="Words from somewhere far. They hold the dark a little off."),
    "v": dict(name="a recorded voice", kind="san", warmth=0, san=22,
              pick="A voice speaks a tongue you half-know. The thread tightens."),
}

BOCSEA = "*"  # the lost-and-refound bundle — the container itself


def spawn_items(rng):
    """Return a list of (x, y, glyph) item drops plus one boccea, on
    walkable ground scattered away from the start."""
    from .config import MAP_W, MAP_H
    pool = [(x, y) for y in range(MAP_H) for x in range(MAP_W)]
    rng.shuffle(pool)
    start = (MAP_W // 2, MAP_H - 3)

    def far(p):
        return abs(p[0] - start[0]) + abs(p[1] - start[1]) >= 6

    drops = []
    far_pool = [p for p in pool if far(p)]
    # one boccea always
    if far_pool:
        x, y = far_pool.pop(0)
        drops.append((x, y, BOCSEA))
    # a handful of items
    glyphs = list(ITEMS.keys())
    for _ in range(rng.randint(5, 9)):
        if not far_pool:
            break
        x, y = far_pool.pop(0)
        drops.append((x, y, rng.choice(glyphs)))
    return drops

"""Core tile definitions and constants."""
from dataclasses import dataclass
import os

# Map dimensions in tiles. Two sizes: 'phone' (fits a phone screen, big glyphs)
# and 'desktop' (a wide street). Select via the SCAINET_MAP env var so the same
# code drives both the phone and desktop versions.
if os.environ.get("SCAINET_MAP") == "desktop":
    MAP_W, MAP_H = 64, 40
else:
    MAP_W, MAP_H = 36, 22

# Curses display offset (leave room for message log / status)
VIEW_OFFSET_Y = 1

# Walkable vs solid tiles
class Tile:
    name = ""
    glyph = " "
    walkable = False
    blocks_fov = True
    color = 1  # curses color pair index (0 = default)

    @classmethod
    def render(cls):
        return cls.glyph


@dataclass(frozen=True)
class T:
    NONE = None
    WALL = 1
    FLOOR = 2
    DOOR = 3
    WATER = 4
    GRASS = 5
    TREE = 6


TILE_CHARS = {
    "#": "wall",
    ".": "floor",
    "+": "door",
    "~": "water",
    ",": "grass",
    "^": "tree",
    " ": "empty",
}


CURSE_COLORS = {
    "default": -1,
    "black": 0,
    "red": 1,
    "green": 2,
    "yellow": 3,
    "blue": 4,
    "magenta": 5,
    "cyan": 6,
    "white": 7,
}

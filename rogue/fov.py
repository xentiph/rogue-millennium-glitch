"""Field of view: shadow-casting raycast so the city stays dark & secret.
Returns a set of visible (x,y) within a radius, stopping at walls & trees.
"""
import math
from .config import MAP_W, MAP_H


def opaque(grid, x, y):
    if not (0 <= x < MAP_W and 0 <= y < MAP_H):
        return True
    return grid[y][x] in ("#", "^")


def compute_fov(grid, px, py, radius):
    visible = set()
    if not (0 <= px < MAP_W and 0 <= py < MAP_H):
        return visible
    visible.add((px, py))
    cells = int(2 * math.pi * radius)
    for i in range(cells):
        ang = (2 * math.pi * i) / cells
        for step in range(1, radius + 1):
            x = px + round(math.cos(ang) * step)
            y = py + round(math.sin(ang) * step)
            if not (0 <= x < MAP_W and 0 <= y < MAP_H):
                break
            visible.add((x, y))
            if opaque(grid, x, y):
                break
    return visible

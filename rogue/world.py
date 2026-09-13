"""New York street generator — a place to meet people, not fight them.
Buildings, doors, puddles, a pocket park, and safe spaces.
Rooms = building footprints; NPCs and ScaiNet nodes are placed by main.
"""
import random

from .config import MAP_W, MAP_H


def empty_grid():
    """Start fully as street/pavement '.'."""
    return [["." for _ in range(MAP_W)] for _ in range(MAP_H)]


def carve_building(grid, x, y, w, h):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            if 0 < xx < MAP_W - 1 and 0 < yy < MAP_H - 1:
                if xx in (x, x + w - 1) or yy in (y, y + h - 1):
                    grid[yy][xx] = "#"
                else:
                    grid[yy][xx] = "." if random.random() < 0.65 else "#"


def place_doors(grid, x, y, w, h):
    n = random.randint(1, 3)
    for _ in range(n):
        side = random.choice("nswe")
        if side == "n":
            sx, sy = random.randint(x + 1, x + w - 2), y
        elif side == "s":
            sx, sy = random.randint(x + 1, x + w - 2), y + h - 1
        elif side == "w":
            sx, sy = x, random.randint(y + 1, y + h - 2)
        else:
            sx, sy = x + w - 1, random.randint(y + 1, y + h - 2)
        if 0 < sx < MAP_W - 1 and 0 < sy < MAP_H - 1 and grid[sy][sx] == "#":
            grid[sy][sx] = "+"


def scatter_city(grid, buildings):
    # puddles
    for _ in range(random.randint(4, 9)):
        x, y = random.randint(1, MAP_W - 2), random.randint(1, MAP_H - 2)
        if grid[y][x] == ".":
            grid[y][x] = "~"
    # trash / newspapers to read (they carry language fragments)
    for _ in range(random.randint(5, 11)):
        x, y = random.randint(1, MAP_W - 2), random.randint(1, MAP_H - 2)
        if grid[y][x] == ".":
            grid[y][x] = "%"
    # pocket park
    x0, y0 = random.randint(2, MAP_W - 10), random.randint(2, MAP_H - 6)
    for yy in range(y0, y0 + 4):
        for xx in range(x0, x0 + 8):
            if 0 < xx < MAP_W - 1 and 0 < yy < MAP_H - 1 and grid[yy][xx] == ".":
                if random.random() < 0.35:
                    grid[yy][xx] = "^"
                elif random.random() < 0.5:
                    grid[yy][xx] = ","
    return grid


def generate_map(rng):
    grid = empty_grid()
    buildings = []
    attempts = 0
    while len(buildings) < 9 and attempts < 300:
        attempts += 1
        w, h = rng.randint(6, 12), rng.randint(5, 9)
        x, y = rng.randint(1, MAP_W - w - 1), rng.randint(1, MAP_H - h - 1)
        new = (x, y, w, h)
        if not any(
            not (new[0]+new[2] <= b[0]+1 or b[0]+b[2] <= new[0]+1
                 or new[1]+new[3] <= b[1]+1 or b[1]+b[3] <= new[1]+1)
            for b in buildings
        ):
            buildings.append(new)
            carve_building(grid, *new)
    for b in buildings:
        place_doors(grid, *b)
    scatter_city(grid, buildings)
    return grid, buildings

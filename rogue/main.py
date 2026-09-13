"""SCAINET — a no-combat language pilgrimage as hard as Spelunky 2.

Octavia, trans Black, wakes under a fallen tarp in New York knowing only
English. There is no combat. The difficulty is language: find the teachers,
learn the five tongues, keep them alive through decay, and hold Sanity,
Warmth, and the drone's charge above zero long enough to reach Nanjing.

Permadeath. One run. The world is different every time.

Run:  cd ~/rogue && python3 -m rogue.main
"""
import curses
import random

from .config import MAP_W, MAP_H, VIEW_OFFSET_Y
from .world import generate_map
from .mutations import Survivor
from .lang import get, LANGS
from .entities import Player, NPC
from .fov import compute_fov
from . import scai
from .items import ITEMS, BOCSEA, spawn_items
from . import procedural as proc
from . import intro

COLOR_PAIRS = {}
LIGHT_TILES = {".", ",", "%", "~"}

# Tongues that must be learned, in the order the world grows harsher.
TONGUES = ["ro", "es", "zh", "ru", "tr", "ar", "fr"]

# NPC glyph + color + a short English flavor per tongue teacher.
TEACHER_STYLE = {
    "ro": ("m", "magenta", "an old busker"),
    "es": ("M", "yellow", "a street cook"),
    "zh": ("W", "cyan", "a shuttered grocer"),
    "ru": ("r", "red", "a late-night nurse"),
    "tr": ("R", "green", "a dockworker at rest"),
    "ar": ("A", "blue", "a desert elder"),
    "fr": ("F", "white", "a patient clerk"),
}

# NPC greeting lines, in their tongue — the words Octavia must learn to hold.
TEACHER_LINES = {
    "ro": "Bună. Te ascult.",
    "es": "Hola. Te escucho.",
    "zh": "你好。我在听。",
    "ru": "Здравствуй. Я слушаю тебя.",
    "tr": "Merhaba. Dinliyorum.",
    "ar": "أهلاً. أنا أسمعك.",
    "fr": "Bonjour. Je t'écoute.",
}


def init_colors():
    curses.start_color()
    curses.use_default_colors()
    pairs = {
        "white": (curses.COLOR_WHITE, -1),
        "red": (curses.COLOR_RED, -1),
        "green": (curses.COLOR_GREEN, -1),
        "yellow": (curses.COLOR_YELLOW, -1),
        "blue": (curses.COLOR_BLUE, -1),
        "magenta": (curses.COLOR_MAGENTA, -1),
        "cyan": (curses.COLOR_CYAN, -1),
        "gray": (curses.COLOR_WHITE, -1),
        "black_on_light": (curses.COLOR_BLACK, curses.COLOR_WHITE),
    }
    idx = 100
    for name, (fg, bg) in pairs.items():
        curses.init_pair(idx, fg, bg)
        COLOR_PAIRS[name] = idx
        idx += 1


def cpair(name):
    return curses.color_pair(COLOR_PAIRS.get(name, 0))


def city_color(ch):
    return {
        "#": "gray", ".": "white", "+": "yellow", "~": "cyan",
        "%": "green", "^": "green", ",": "green",
    }.get(ch, "white")


def player_pair(under_tile):
    return cpair("black_on_light") if under_tile in LIGHT_TILES else cpair("white")


def render(stdscr, grid, player, npcs, nodes, visible, log, status, cam=None, drops=()):
    """Render the viewport. cam = [cam_dx, cam_dy] offset (pan).
    Text rendering scales with drone altitude: the higher the drone flies,
    the more message rows Octavia can read at once.
    """
    stdscr.erase()
    mh, mw = stdscr.getmaxyx()          # terminal size
    alt = player.drone.altitude         # 1..5
    # message rows scale with altitude (1 row at low, 5 at full height)
    log_rows = max(1, min(5, alt))
    hud_rows = 2                        # one for messages, one for status
    vh = max(4, mh - log_rows - hud_rows)
    vw = mw
    cx = player.x + (cam[0] if cam else 0)
    cy = player.y + (cam[1] if cam else 0)
    ox = cx - vw // 2
    oy = cy - vh // 2
    ox = max(0, min(ox, max(0, MAP_W - vw)))
    oy = max(0, min(oy, max(0, MAP_H - vh)))

    def draw_tile(mx, my, ch, c):
        sx = mx - ox
        sy = my - oy
        if 0 <= sx < vw and 0 <= sy < vh:
            try:
                stdscr.addnstr(sy + VIEW_OFFSET_Y, sx, ch, 1, c)
            except curses.error:
                pass

    for my in range(oy, min(MAP_H, oy + vh)):
        for mx in range(ox, min(MAP_W, ox + vw)):
            if (mx, my) not in visible:
                continue
            draw_tile(mx, my, grid[my][mx], cpair(city_color(grid[my][mx])))
    for (nx, ny) in nodes:
        if (nx, ny) in visible:
            draw_tile(nx, ny, "O", cpair("green") | curses.A_BOLD)
    for npc in npcs:
        if npc.x >= 0 and (npc.x, npc.y) in visible:
            draw_tile(npc.x, npc.y, npc.glyph, cpair(npc.color))
    # item drops on the ground (only ones not yet taken)
    for (ix, iy, iglyph) in drops:
        if (ix, iy) in visible:
            draw_tile(ix, iy, iglyph, cpair("yellow"))
    if player.x >= 0:
        under = grid[player.y][player.x]
        draw_tile(player.x, player.y, "@", player_pair(under) | curses.A_BOLD)
    if player.drone.alive and player.drone.revealed:
        # the drone is the eye above Octavia — it hangs directly overhead,
        # surveilling. It only slides to the side when a wall blocks its view,
        # so it never loses sight of her.
        px, py = player.x, player.y
        above = (px, py - 1)
        if 0 <= above[1] < MAP_H and grid[above[1]][above[0]] == "#":
            # wall overhead — flank to the side that stays open
            for sx in (-1, 1):
                side = (px + sx, py - 1)
                if 0 <= side[0] < MAP_W and grid[side[1]][side[0]] in (".", ",", "%", "~"):
                    above = side
                    break
        if above in visible and 0 <= above[0] < MAP_W and 0 <= above[1] < MAP_H:
            draw_tile(above[0], above[1], "d", cpair("cyan"))

    # ---- help panel on the right: only while still in the first
    # environment (before Octavia meets her first wall / the drone reveals).
    # It fades once the real journey begins.
    if not player.drone.revealed:
        help_x = max(0, mw - 22)
        help_lines = [
            "  hjkl/arrows  move",
            "      t        talk",
            "      l        listen/learn",
            "      b        use body item",
            "      s        use mind item",
            "      .        rest",
            "      c        recenter cam",
            "      q        quit",
            "",
            "  meet a soul who",
            "  speaks a tongue.",
            "  open your hand.",
        ]
        for i, ln in enumerate(help_lines):
            y = 1 + i
            if y >= mh:
                break
            c = "green" if "hjkl" in ln or "open your hand" in ln else "gray"
            try:
                stdscr.addnstr(y, help_x, ln[:21], 21, cpair(c))
            except curses.error:
                pass

    # ---- message log: full text, wrapped, rows scale with altitude ----
    def wrap(text, width):
        words = text.split()
        lines, cur = [], ""
        for w in words:
            if cur and len(cur) + 1 + len(w) > width:
                lines.append(cur)
                cur = w
            else:
                cur = (cur + " " + w).strip()
        if cur:
            lines.append(cur)
        return lines

    try:
        # recent messages, newest first, up to log_rows deep
        recent = [m for m in log[-8:]][::-1]
        placed = 0
        for msg in recent:
            if placed >= log_rows:
                break
            for ln in wrap(msg, mw - 2):
                if placed >= log_rows:
                    break
                row_y = mh - log_rows - 1 + placed
                stdscr.addnstr(row_y, 1, ln[: mw - 2], mw - 2, cpair("gray"))
                placed += 1
        # status line — shows resources AND drone altitude
        status_str = status(player)
        stdscr.addnstr(mh - 1, 0, status_str[: mw - 1], mw - 1, cpair("cyan"))
    except curses.error:
        pass
    stdscr.refresh()


def place_things(grid, buildings, rng):
    """Return (npcs, nodes). Every tongue has a teacher, generated
    procedurally by the small model — each with a hidden soul identity.
    All scattered at random walkable points, never next to the start."""
    npcs, nodes = [], []
    pool = [(x, y) for y in range(MAP_H) for x in range(MAP_W)
            if grid[y][x] == "."]
    rng.shuffle(pool)
    start = (MAP_W // 2, MAP_H - 3)
    def far(p, min_d=9):
        return abs(p[0] - start[0]) + abs(p[1] - start[1]) >= min_d
    far_pool = [p for p in pool if far(p)]
    # teachers — procedurally generated, one per tongue
    for i, t in enumerate(TONGUES):
        if not far_pool:
            break
        tgen = proc.make_teacher(i, rng)
        x, y = far_pool.pop(0)
        npcs.append(NPC(tgen["glyph"], tgen["color"], tgen["alias"],
                        x, y, tgen["tongue"], tgen["line"], soul=tgen["soul"]))
    # ScaiNet safe nodes (safety is scarce: fewer than teachers)
    safe_count = rng.randint(2, 3)
    for _ in range(safe_count):
        if far_pool:
            nodes.append(far_pool.pop(0))
    return npcs, nodes


def new_run(rng):
    """Start a fresh permadeath run. Returns everything."""
    grid, buildings = generate_map(rng)
    survivor = Survivor(rng)
    start = (MAP_W // 2, MAP_H - 3)
    player = Player(start[0], start[1], survivor, openness=15, faith=15)
    npcs, nodes = place_things(grid, buildings, rng)
    drops = spawn_items(rng)
    return grid, buildings, survivor, player, npcs, nodes, drops


def show_intro(stdscr):
    """Draw the face of the world (the launch screen), wait for a key."""
    stdscr.clear()
    mh, mw = stdscr.getmaxyx()
    rows = intro.FACE
    # center vertically
    top = max(0, (mh - len(rows)) // 2)
    for i, (text, color) in enumerate(rows):
        y = top + i
        if y >= mh:
            break
        col = {"eye": "green", "core": "white", "dim": "green"}.get(color, "green")
        try:
            stdscr.addnstr(y, max(0, (mw - len(text)) // 2), text,
                           mw - 1, cpair(col) | (curses.A_BOLD if color in ("eye", "core") else 0))
        except curses.error:
            pass
    stdscr.refresh()
    # wait for any key
    while True:
        k = stdscr.getch()
        if k != -1 and k != curses.KEY_MOUSE:
            return
        # keep redrawing in case of a key we don't handle (e.g. resize blips)
        if k == curses.KEY_MOUSE:
            break


def main(stdscr):
    init_colors()
    curses.curs_set(0)
    show_intro(stdscr)
    rng = random.Random()

    grid, buildings, survivor, player, npcs, nodes, drops = new_run(rng)

    clock = 0
    game_over = False
    dead_reason = ""
    cam = [0, 0]                     # camera pan offset (click-drag)
    press_start = None               # screen coord where the drag began

    log = [get("en", "wake_1"), get("en", "wake_2"),
           survivor.describe(),
           "You know only English. The world waits for your words.",
           "Your boccea is gone. Until you find one (*), you can only use what "
           "you can carry in the moment."]
    status = lambda p: (
        f"Dawn {clock}/24  Sanity {p.sanity:3d}  Warmth {p.warmth:3d}  "
        f"Open {p.openness}  Faith {p.faith}  Drone {p.drone.charge}  "
        f"Stash {'+'.join(sorted(p.inventory)) or '-'}  "
        f"Tongues: {','.join(sorted(p.known)) or '-'}")

    # enable mouse capture — wheel flies the drone, drag pans the map
    try:
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
    except curses.error:
        pass

    # drone altitude sets how far Octavia can see
    player.vision = player.drone.radius()

    while True:
        # resources drain slowly — but each passing hour of the day bites
        # harder. A winning run is one full crossing; dawdle deeper into the
        # night and the street tightens around Octavia.
        _ramp = {0: 12, 6: 9, 12: 6, 18: 4}
        _hour = max(h for h in _ramp if clock >= h)
        drain_every = _ramp.get(_hour, 12)
        if not game_over and player.x >= 0:
            if clock % drain_every == 0:
                player.sanity = max(0, player.sanity - 1)
                player.warmth = max(0, player.warmth - 1)
            player.drone.drain()
            if player.sanity <= 0:
                game_over, dead_reason = True, "the loneliness ate your mind"
            elif player.warmth <= 0:
                game_over, dead_reason = True, "the cold won in the end"
            elif player.drone.charge <= 0:
                game_over, dead_reason = True, "the drone went dark; the road is lost"

        visible = compute_fov(grid, player.x, player.y, player.vision)
        render(stdscr, grid, player, npcs, nodes, visible, log, status, cam, drops)

        k = stdscr.getch()
        if k == curses.KEY_MOUSE:
            try:
                _, mx, my, _, bstate = curses.getmouse()
            except curses.error:
                continue
            # safe bit check — not every macOS build defines every button const
            def bit(name):
                return getattr(curses, name, 0)
            try:
                if bstate & bit("BUTTON4_PRESSED"):        # wheel up
                    player.drone.rise()
                    player.vision = player.drone.radius()
                    log.append(f"The drone climbs. alt {player.drone.altitude}/5")
                elif bstate & bit("BUTTON5_PRESSED"):      # wheel down
                    player.drone.sink()
                    player.vision = player.drone.radius()
                    log.append(f"The drone sinks low. alt {player.drone.altitude}/5")
                elif bstate & bit("BUTTON1_PRESSED"):
                    press_start = (mx, my)
                elif (bstate & bit("BUTTON1_RELEASED")) and press_start:
                    cam[0] += (press_start[0] - mx)
                    cam[1] += (press_start[1] - my)
                    press_start = None
                elif bstate & bit("BUTTON2_PRESSED"):
                    cam[0], cam[1] = 0, 0
                    log.append("The camera returns to Octavia.")
            except Exception:                              # never crash the session
                pass
            continue
        # altitude + camera via keyboard (always works, even with no mouse)
        if k in (ord("["), ord("e")):
            player.drone.rise()
            player.vision = player.drone.radius()
            log.append(f"The drone climbs. More of the street opens. (alt {player.drone.altitude}/5)")
            continue
        if k in (ord("]"), ord("f")):
            player.drone.sink()
            player.vision = player.drone.radius()
            log.append(f"The drone sinks low. The street narrows. (alt {player.drone.altitude}/5)")
            continue
        if k == ord("c"):
            cam[0], cam[1] = 0, 0
            log.append("The camera returns to Octavia.")
            continue
        if k == ord("q"):
            break
        if game_over:
            stdscr.clear()
            stdscr.addnstr(MAP_H // 2 - 1, 2,
                           f"run {clock}+ over: {dead_reason}.", 76, cpair("red"))
            stdscr.addnstr(MAP_H // 2, 2, "[n]ew run   [q]uit", 76, cpair("white"))
            stdscr.refresh()
            while True:
                k2 = stdscr.getch()
                if k2 == ord("n"):
                    grid, buildings, survivor, player, npcs, nodes, drops = new_run(rng)
                    log = [get("en", "wake_1"), get("en", "wake_2"),
                           survivor.describe(),
                           "You know only English. The world waits for your words."]
                    game_over = False
                    clock = 0
                    break
                if k2 == ord("q"):
                    return
            continue

        dx = dy = 0
        if k in (ord("h"), curses.KEY_LEFT):
            dx = -1
        elif k in (ord("l"), curses.KEY_RIGHT):
            dx = 1
        elif k in (ord("k"), curses.KEY_UP):
            dy = -1
        elif k in (ord("j"), curses.KEY_DOWN):
            dy = 1
        elif k == ord("."):
            # rest a beat — a slow learner needs patience to make 100 hours
            player.sanity = min(player.sanity + 2, 100)
            player.warmth = min(player.warmth + 2, 100)
            dx = dy = 0
        elif k == ord("t"):
            # talk to the nearest adjacent NPC
            target = None
            for npc in npcs:
                if npc.x >= 0 and abs(npc.x - player.x) + abs(npc.y - player.y) <= 1:
                    target = npc
                    break
            if target:
                if target.tongue in player.known:
                    log.append(f"You speak her {LANGS[target.tongue]}: "
                               f"{target.line}")
                    player.speak(target.tongue)
                else:
                    log.append(f"You don't know {LANGS[target.tongue]}."
                               f" She says: \"{target.line}\"")
                    log.append("How do you answer her words?")
                    log.append("  1 open fear, 2 open a little, 3 answer with rage")
                    stdscr.refresh()
                    try:
                        ck = stdscr.getch()
                    except curses.error:
                        ck = 0
                    if ck == ord("1"):
                        f = player.show_emotion("fear")
                        log.append("You flinch and look away. Faith wavers.")
                        log.append(f"Faith {f} — she reads your fear and keeps her words close.")
                    elif ck == ord("2"):
                        f = player.show_emotion("open")
                        log.append("You meet her gaze, unsure but willing.")
                        log.append(f"Faith {f} — the thread between you tightens.")
                    elif ck == ord("3"):
                        f = player.show_emotion("anger")
                        log.append("Your jaw sets. The old anger answers for you.")
                        log.append(f"Faith {f} — she steps back, guarding what she knows.")
                    else:
                        f = player.show_emotion("fear")
                        log.append("You say nothing, and the silence answers fear.")
                    if player.faith >= 55:
                        player.learn(target.tongue)
                        player.sanity = min(player.sanity + 10, 100)
                        log.append(f"In trusting a little, her {LANGS[target.tongue]} "
                                   f"settles into you. learned: {LANGS[target.tongue]}")
                        # past-life memory — high faith lets her recall a soul
                        # who helped her before. That is how trust is learned.
                        soul_key = target.soul["name"]
                        if player.faith >= 70 and soul_key not in player.remembered_souls:
                            player.remembered_souls.add(soul_key)
                            log.append(proc.MEMORY_FLASH.format(
                                soul=target.soul["name"],
                                helped=target.soul["helped"]))
                            log.append("Openness grows. Trust, it seems, is carried "
                                       "across the dark too. (+openness)")
                            player.openness = min(100, player.openness + 6)
                            player.faith = min(100, player.faith + 5)
                    else:
                        log.append(f"You need faith above {55} to learn her tongue. "
                                   f"(Faith {player.faith})")
            else:
                log.append("No one is close enough to talk to.")
            continue
        elif k == ord("l"):
            # listen / learn from nearest adjacent teacher
            target = None
            for npc in npcs:
                if npc.x >= 0 and npc.tongue not in player.known \
                   and abs(npc.x - player.x) + abs(npc.y - player.y) <= 1:
                    target = npc
                    break
            if target:
                player.learn(target.tongue)
                player.sanity = min(player.sanity + 15, 100)
                log.append(f"You listen hard. Her {LANGS[target.tongue]} begins "
                           f"to settle in your mouth.")
                log.append(f"learned: {LANGS[target.tongue]}")
            else:
                log.append("No one nearby is willing to teach right now.")
            continue

        if k == ord("b"):
            item = player.use_for_body()
            if item:
                log.append(ITEMS[item]["pick"])
            else:
                log.append("You have nothing in the stash to warm your body.")
            continue
        if k == ord("s"):
            item = player.use_for_sanity()
            if item:
                log.append(ITEMS[item]["pick"])
            else:
                log.append("You have nothing in the stash to steady your mind.")
            continue

        if dx or dy:
            nx, ny = player.x + dx, player.y + dy
            if not (0 <= nx < MAP_W and 0 <= ny < MAP_H):
                continue
            ch = grid[ny][nx]
            if ch == "#":
                log.append("A wall of cold brick. The city doesn't open.")
                # the saviours shift to keep watch — the first wall reveals them
                if not player.drone.revealed:
                    player.drone.revealed = True
                    log.append("Something hums just over your shoulder, out of sight.")
                    log.append("It was there all along, keeping watch over you.")
            elif ch in ("+", ".", ",", "%", "~"):
                player.x, player.y = nx, ny
                if ch == "%":
                    # trash: sometimes a fragment of any foreign tongue
                    if rng.random() < 0.3:
                        frag = rng.choice(TONGUES)
                        log.append(f"A damp paper: a few words in {LANGS[frag]}."
                                   if frag not in player.known else
                                   f"A paper you already understand ({LANGS[frag]}).")
                        if frag not in player.known:
                            player.learn(frag)
                            player.sanity = min(player.sanity + 10, 100)
                            log.append(f"learned: {LANGS[frag]}")
                elif ch == "~":
                    log.append("Cold rainwater soaks your shoes. Warmth sinks.")
                    player.warmth = max(0, player.warmth - 3)
            # pick up an item lying on the ground here
            drop_here = [d for d in drops if d[0] == player.x and d[1] == player.y]
            for d in list(drop_here):
                if d[2] == BOCSEA:
                    player.has_boccea = True
                    log.append("You find your boccea caught in a gate."
                               " Now you can carry what the world leaves you.")
                else:
                    if player.has_boccea:
                        player.inventory.append(d[2])
                        log.append(f"Picked up {ITEMS[d[2]]['name']} (b/s to use).")
                    else:
                        # no boccea yet — forced to use in the moment
                        it = ITEMS[d[2]]
                        player.warmth = min(100, player.warmth + it["warmth"])
                        player.sanity = min(100, player.sanity + it["san"])
                        log.append(f"No boccea to carry it — {it['pick']}")
                drops.remove(d)
            # standing on a ScaiNet safe node recharges body and drone
            if (player.x, player.y) in nodes and player.x >= 0:
                player.sanity = min(player.sanity + 20, 100)
                player.warmth = min(player.warmth + 15, 100)
                player.drone.recharge()
                log.append("Green light hums at your feet. The oracle shelters you.")
                log.append("san +, warmth +, drone recharged.")
                # remove the node once fully used
                nodes.remove((player.x, player.y))

        clock += 1

        # retention decay: forget a learned tongue if you don't speak enough
        if not game_over:
            for t in list(player.known - {"en"}):
                if rng.random() < 0.004:  # slow — it's a hard game, not cheap
                    player.known.discard(t)
                    log.append(f"The {LANGS[t]} words loose their grip. "
                               f"You forget {LANGS[t]}. Find a teacher again.")

        # a winning run is ONE full day of the crossing: the 24th hour, all
        # seven tongues in her mouth, and the drone still watching over her.
        needed = {"ro", "es", "zh", "ru", "tr", "ar", "fr"}
        if clock >= 24 \
           and player.drone.alive and player.drone.charge > 0 \
           and player.known >= needed:
            game_over = True
            dead_reason = ""
            break

    # Nanjing ending
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    lines = ["", get("en", "nanking_1"), "", get("en", "nanking_2"), "",
             get("en", "nanking_3"), get("en", "nanking_4"),
             get("en", "nanking_5"), "", "octavia — ", "",
             get("en", "nanking_6"), ""]
    y = (h - len(lines)) // 2
    for ln in lines:
        if y < h:
            color = "green" if "octavia" in ln else "gray"
            stdscr.addnstr(y, max(2, (w - len(ln)) // 2), ln[: w - 4], w - 4,
                           cpair(color))
        y += 1
    stdscr.refresh()
    stdscr.getch()


def run():
    curses.wrapper(main)


if __name__ == "__main__":
    run()

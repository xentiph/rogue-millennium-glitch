"""Entities — there is no combat in Scainet.
The difficulty is language. Octavia meets people, and every person speaks
a tongue. To move on, she must find someone who can teach her the words.

Entities are NPCs (who they are + the tongue they speak) and the drone.
"""
import random
from .items import ITEMS


class NPC:
    """A person who speaks a tongue. Talking can teach it to Octavia.
    Each NPC has a present-life alias AND a deeper 'soul' that persists across
    runs. When Octavia's faith is high, she remembers souls who helped her in
    past lives — that is how she learns to trust."""
    def __init__(self, glyph, color, name, x, y, tongue, line, soul=None):
        self.glyph = glyph
        self.color = color
        self.name = name           # alias in the present life
        self.x = x
        self.y = y
        self.tongue = tongue       # 'ro','es','zh','ru','tr'
        self.line = line           # a greeting in that tongue (from lang)
        self.taught = False        # has Octavia learned from them?
        self.ai = "wander"
        self.soul = soul or {"name": name, "helped": "held a door when the night came"}
        self.remembered = False    # has Octavia recalled this soul from a past life?

    def dist(self, ox, oy):
        return abs(self.x - ox) + abs(self.y - oy)


class Drone:
    """Octavia's little companion. No combat — it carries light and company,
    and needs to recharge at a ScaiNet safe node.
    It flies. The higher it rises, the wider Octavia can see (perspective)."""
    def __init__(self):
        self.name = "drone"
        self.charge = 100
        self.alive = True
        self.altitude = 1        # 1 low .. 5 high — controls sight radius
        self.revealed = False    # Octavia doesn't know the drone exists at first

    def drain(self):
        self.charge = max(0, self.charge - 1)

    def recharge(self):
        self.charge = min(100, self.charge + 25)

    def rise(self, n=1):
        """Fly higher: Octavia sees farther. Costs a little charge to climb."""
        if self.charge <= 0:
            return False
        old = self.altitude
        self.altitude = max(1, min(5, self.altitude + n))
        self.charge = max(0, self.charge - (self.altitude - old) if self.altitude > old else self.charge)
        return self.altitude != old

    def sink(self, n=1):
        old = self.altitude
        self.altitude = max(1, min(5, self.altitude - n))
        return self.altitude != old

    def radius(self):
        """Sight radius grows with altitude."""
        return 4 + self.altitude * 2   # 6,8,10,12,14


class Player:
    """Octavia. Starts knowing only English; learns the tongues of the world.
    She has lost her boccea — she begins with no container, so she can only
    hold/use items once she finds a new one (`*`)."""

    def knows(self, tongue):
        return tongue in self.known

    def learn(self, tongue):
        self.known.add(tongue)

    def speak(self, tongue):
        self.learning = tongue

    # ---- item / boccea system ----
    # inventory dict: glyph -> {'name','kind','warmth','san','pick'}
    def __init__(self, x, y, origin, has_boccea_start=False,
                 openness=None, faith=None):
        self.glyph = "@"
        self.name = "Octavia"
        self.x = x
        self.y = y
        self.origin = origin
        self.known = {"en"}
        self.learning = None
        self.drone = Drone()
        self.sanity = 100
        self.warmth = 100
        self.vision = 7
        # the soul starts having LOST their boccea — so they begin with
        # no container: anything found is consumed on the spot.
        self.has_boccea = has_boccea_start
        self.inventory = []           # carried (glyph) items when a boccea is held
        # ---- openness / faith ----
        # openness: how far the soul lets the world in (0 closed .. 100 trusting)
        # faith: living trust, spent by fear/anger, restored by openness
        self.openness = openness if openness is not None else 25   # Octavia starts shut
        self.faith = faith if faith is not None else self.openness
        # souls this player has already remembered from past lives
        self.remembered_souls = set()

    def show_emotion(self, emotion):
        """A dialogue choice. Calm/open builds faith; fear/anger burns it."""
        if emotion == "open":
            self.faith = min(100, self.faith + 6)
            self.openness = min(100, self.openness + 3)
        elif emotion == "fear":
            self.faith = max(0, self.faith - 10)
            self.openness = max(0, self.openness - 4)
        elif emotion == "anger":
            self.faith = max(0, self.faith - 14)
            self.openness = max(0, self.openness - 6)
        return self.faith

    def use_for_body(self):
        """Use a carried body item for warmth."""
        for it in self.inventory:
            if ITEMS[it]["kind"] == "body":
                self.inventory.remove(it)
                self.warmth = min(100, self.warmth + ITEMS[it]["warmth"])
                return it
        return None

    def use_for_sanity(self):
        for it in self.inventory:
            if ITEMS[it]["kind"] == "san":
                self.inventory.remove(it)
                self.sanity = min(100, self.sanity + ITEMS[it]["san"])
                return it
        return None

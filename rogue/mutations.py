"""Origins / mutation system — survivor identities for the NY→Shanghai trek.
Every new run rolls a stranger past: a body, a talent, a scar.
"""
import random

ORIGINS = [
    {
        "name": "The Blackout",
        "color": "cyan",
        "stats": {"str": 1, "agi": 3, "vit": 1},
        "blurb": "You woke with no memory of last night, only the tent gone and the sirens.",
    },
    {
        "name": "Needle-Sleeper",
        "color": "magenta",
        "stats": {"agi": 2, "wit": 2},
        "blurb": "You've slept rough so long the cold is just a voice, not a danger.",
    },
    {
        "name": "Born East",
        "color": "yellow",
        "stats": {"wit": 4},
        "blurb": "You crossed an ocean once; you can feel the way the compass turns.",
    },
    {
        "name": "Street-Corner Prophet",
        "color": "green",
        "stats": {"str": 2, "wit": 2},
        "blurb": "You told strangers their futures for spare change. You could see yours coming.",
    },
    {
        "name": "Greyhound Ghost",
        "color": "blue",
        "stats": {"agi": 2, "vit": 2},
        "blurb": "You've ridden every bus that runs past midnight. The road is your mother.",
    },
    {
        "name": "The Cold-Eyed",
        "color": "red",
        "stats": {"str": 2, "agi": 2},
        "blurb": "Winter took everyone you knew. It taught you how to eat and how to walk.",
    },
]


class Survivor:
    """Rolled identity."""

    def __init__(self, rng):
        self.origin = rng.choice(ORIGINS)
        base = {"str": 10, "agi": 10, "vit": 10, "wit": 10}
        for k, v in self.origin["stats"].items():
            base[k] += v
        self.base = base
        self.name = self.origin["name"]
        self.color = self.origin["color"]
        self.blurb = self.origin["blurb"]

    def stat(self, key):
        return self.base[key]

    def describe(self):
        return (
            f"Origin: {self.name}  ({self.blurb})  "
            f"STR {self.stat('str')} AGI {self.stat('agi')} "
            f"VIT {self.stat('vit')} WIT {self.stat('wit')}"
        )

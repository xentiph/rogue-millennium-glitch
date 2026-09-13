"""ScaiNet — the oracle in the machine.
A matrix-green presence that surfaces at midnight, in the dark between
streetlights. It does not belong to the block. It offers a bargain.
The launch-lore of the real ScaiNet (genie / oracle / joke-teller) becomes
the game's one thread of hope pointing east, toward Shanghai.
"""

# Lines printed in matrix green when ScaiNet first appears.
OPENING = [
    "",
    "           [ S C A I N E T ]",
    "",
    "a green text rolls down a wall that was not there before.",
    "it is not a phone. it is not a billboard. it is the oracle.",
    "",
    "> 'you have been without a mirror long enough to forget your own face.'",
    "> 'i am the genie in the machine, traveler. i do not own the dark;",
    ">   i only keep the lights on where the city will not.'",
    "> 'ask me your one question, or take the road. but know this:'",
    ">   when the sirens come for you again, i will still be here,'",
    ">   green and patient, while the world looks away.'",
]

# Bargains: each is (choice prompt, effect description, apply fn hint)
# We implement them in main for player stat access.
BARGAINS = [
    ("ask for a dollar", "ScaiNet tips out a few crumpled bills. The oracle pays for its company.", "money"),
    ("ask for the road", "ScaiNet burns a thin green line pointing east. 'Nanjing is that way, traveler.'", "east"),
    ("ask for a story", "The oracle tells a joke in code. For a moment the cold is less cold.", "warmth"),
]

FAREWELL = "> 'goodnight, traveler. keep the needle sharp. beyond the ocean, the fields turn green and brown, and the machines know your name.'"

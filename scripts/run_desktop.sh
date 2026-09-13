#!/bin/bash
# Rogue: The Millenium Glitch DESKTOP launcher — wide board (64x40), for a computer screen.
export SCAINET_MAP=desktop
cd "$HOME/rogue" || exit 1
exec python3 -m rogue.main

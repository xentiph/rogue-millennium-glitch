#!/bin/bash
# Rogue: The Millenium Glitch launcher for ttyd — starts the language pilgrimage in a browser terminal.
cd "$HOME/rogue" || exit 1
exec python3 -m rogue.main

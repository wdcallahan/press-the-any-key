#!/usr/bin/env bash
#
# gnome-press-the-any-key
# Copyright 2026 W. D. Callahan II
#
# SPDX-License-Identifier: GPL-3.0-or-later

SOCKET="${XDG_RUNTIME_DIR}/.ydotool_socket"

# Ensure ydotoold is available
if [[ ! -S "$SOCKET" ]]; then
    systemctl --user start ydotool.service

    # Wait for socket to appear
    for _ in {1..20}; do
        [[ -S "$SOCKET" ]] && break
        sleep 0.1
    done
fi

# Final sanity check
if [[ ! -S "$SOCKET" ]]; then
    echo "ERROR: ydotool socket did not appear." >&2
    exit 1
fi

# Generate random alphanumeric
chars=({a..z} {A..Z} {0..9})
rand=${chars[$RANDOM % ${#chars[@]}]}

# Inject it
ydotool type "$rand"

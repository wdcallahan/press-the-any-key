#!/usr/bin/env bash
#
# gnome-press-the-any-key
# Copyright 2026 W. D. Callahan II
#
# SPDX-License-Identifier: GPL-3.0-or-later

SERVICE="ydotool.service"

# A stopped ydotoold can leave its socket pathname behind. Check the service
# itself rather than treating a socket node as proof that the daemon is alive.
if ! systemctl --user is-active --quiet "$SERVICE"; then
    systemctl --user reset-failed "$SERVICE"
    systemctl --user start "$SERVICE"
fi

# Generate random alphanumeric
chars=({a..z} {A..Z} {0..9})
rand=${chars[$RANDOM % ${#chars[@]}]}

# Type only after ydotoold is actually ready. This also covers the brief
# startup window where the service is active but its socket is not yet usable.
for _ in {1..50}; do
    if ydotool type "$rand" 2>/dev/null; then
        exit 0
    fi

    if ! systemctl --user is-active --quiet "$SERVICE"; then
        systemctl --user reset-failed "$SERVICE"
        systemctl --user start "$SERVICE" || true
    fi

    sleep 0.1
done

echo "ERROR: ydotoold did not become ready." >&2
exit 1

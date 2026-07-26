# gnome-press-the-any-key

A GNOME/Wayland "Any Key" implementation using:

* `ydotool`
* GNOME custom shortcuts
* Ansible deployment
* idempotent reconciliation logic

This project began as a joke:

> "I want to relabel a key as Any Key, and when pressed, it should type a random character."

But like many good infrastructure projects, it rapidly escalated into a serious exploration of modern Linux desktop automation under Wayland.

---

## Features

* Wayland-compatible synthetic keyboard input
* GNOME custom shortcut integration
* User-level `ydotoold` service
* Declarative deployment with Ansible
* Idempotent GNOME shortcut reconciliation
* Safe coexistence with unrelated GNOME shortcuts
* Tested on Fedora + GNOME 50

---

## Requirements

Current environment tested:

* Fedora 44
* GNOME 50
* Wayland session
* Python 3.14
* `ydotool`
* access to `/dev/uinput`

Other distributions and desktop environments may work, but are currently untested.

---

## What It Does

The installed shortcut launches `any.sh`, which:

1. Ensures `ydotoold` is running
2. Selects a random alphanumeric character
3. Injects that character through the Wayland-safe `ydotool` input path

Example outputs:

```text
A
7
q
Z
```

The default binding is currently:

```text
F9
```

though this is configurable through role defaults.

## Nova keyboard integration

The standalone role retains `F9` as its portable default. In Nova's current
Lemokey X2 stack, the physical Any tap follows this path instead:

```text
PB_26 → KEY_MACRO26 → XF86Macro26 → GNOME shortcut → any.sh
```

The dual-role key's hold side is Meta and is owned by the firmware/XKB project;
this repository owns only the Any tap's shortcut and synthetic-input path.

The canonical whole-system status and boundaries live in
[`x1_keyboard_layout`](https://github.com/wdcallahan/x1_keyboard_layout):

- [guided tour](https://github.com/wdcallahan/x1_keyboard_layout/blob/main/docs/nova-keyboard-input-architecture.md)
- [technical architecture](https://github.com/wdcallahan/x1_keyboard_layout/blob/main/docs/keyboard-architecture.md)

---

## Project Layout

```text
.
├── playbook.yml
└── roles
    └── any_key
        ├── defaults
        │   └── main.yml
        ├── files
        │   ├── bin
        │   │   └── ensure_gnome_shortcut.py
        │   ├── scripts
        │   │   └── any.sh
        │   └── systemd
        │       └── user
        │           └── ydotool.service
        └── tasks
            └── main.yml
```

---

## Installation

Clone the repository:

```bash
git clone <repo-url>
cd gnome-press-the-any-key
```

Run the playbook:

```bash
ansible-playbook playbook.yml
```

The role will:

* validate the desktop environment
* verify GNOME availability
* verify `ydotool` availability
* install the helper scripts
* install the user service
* enable and start `ydotoold`
* reconcile the GNOME shortcut state

---

## Shortcut Reconciliation

One of the more interesting parts of this project is the GNOME shortcut reconciliation helper:

```text
ensure_gnome_shortcut.py
```

Rather than blindly appending duplicate shortcuts every run, the helper:

* searches existing GNOME custom shortcuts
* identifies managed shortcuts by known fingerprints
* updates existing managed entries in place
* allocates a fresh slot only when necessary
* preserves unrelated user shortcuts

The helper is intentionally idempotent.

Repeated runs should converge to:

```json
{"changed": false}
```

when the system already matches the desired state.

---

## Why This Exists

Classic X11-era automation tools had effectively unrestricted access to desktop input injection.

Wayland deliberately changed that security model.

This project explores what modern desktop automation now looks like when:

* synthetic input is restricted
* desktop environments mediate shortcuts
* services become user-scoped
* reproducibility matters
* configuration management replaces ad-hoc scripting

The result is less of a toy than a tiny reference architecture for:

* desktop automation
* keyboard experimentation
* Wayland-compatible input workflows
* declarative personal workstation configuration

---

## Future Directions

Potential future work:

* generalized keyboard role collection
* Hyper-key integration
* additional desktop environment support
* configurable character sets
* tap/hold integration experiments
* QMK-aware deployment tooling
* complete workstation bootstrap playbooks

---

## License

gnome-press-the-any-key is free software licensed under the GNU General Public License,
version 3 or (at your option) any later version.

Copyright 2026 W. D. Callahan II

See the file COPYING for details.

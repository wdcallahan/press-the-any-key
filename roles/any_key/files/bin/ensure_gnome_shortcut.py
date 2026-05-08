#!/usr/bin/env python3
#
# gnome-press-the-any-key
# Copyright 2026 W. D. Callahan II 
#
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import ast
import json
import subprocess
import sys


BASE_SCHEMA = "org.gnome.settings-daemon.plugins.media-keys"
BINDING_SCHEMA = "org.gnome.settings-daemon.plugins.media-keys.custom-keybinding"
BASE_PATH = "/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/"


def run_gsettings(args):
    result = subprocess.run(
        ["gsettings", *args],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    return result.stdout.strip()


def parse_gvariant(value):
    value = value.strip()

    if value == "true":
        return True

    if value == "false":
        return False
    if value.startswith("@as "):
        value = value[4:]

    return ast.literal_eval(value)


def gsettings_get(schema, key, path=None):
    schema_arg = f"{schema}:{path}" if path else schema
    value = run_gsettings(["get", schema_arg, key])

    return parse_gvariant(value)


def gsettings_set(schema, key, value, path=None):
    schema_arg = f"{schema}:{path}" if path else schema
    run_gsettings(["set", schema_arg, key, value])


def gsettings_string(value):
    return repr(value)


def gsettings_bool(value):
    return "true" if value else "false"


def shortcut_get(path, key):
    try:
        return gsettings_get(BINDING_SCHEMA, key, path)
    except subprocess.CalledProcessError:
        return None


def find_existing_shortcut(paths, desired_name, desired_command, legacy_commands):
    for path in paths:
        current_name = shortcut_get(path, "name")
        current_command = shortcut_get(path, "command")

        name_matches = (
            isinstance(current_name, str)
            and current_name.casefold() == desired_name.casefold()
        )

        command_matches = (
            current_command == desired_command
            or current_command in legacy_commands
        )

        if name_matches and command_matches:
            return path

    return None


def allocate_shortcut_path(paths):
    used_paths = set(paths)
    index = 0

    while True:
        candidate = f"{BASE_PATH}custom{index}/"

        if candidate not in used_paths:
            return candidate

        index += 1


def ensure_shortcut(name, command, binding, legacy_commands):
    changed = False

    paths = gsettings_get(BASE_SCHEMA, "custom-keybindings")

    if not isinstance(paths, list):
        raise RuntimeError("GNOME custom-keybindings setting is not a list")

    shortcut_path = find_existing_shortcut(
        paths=paths,
        desired_name=name,
        desired_command=command,
        legacy_commands=legacy_commands,
    )

    if shortcut_path is None:
        shortcut_path = allocate_shortcut_path(paths)
        paths.append(shortcut_path)
        gsettings_set(BASE_SCHEMA, "custom-keybindings", repr(paths))
        changed = True

    desired_values = {
        "name": name,
        "command": command,
        "binding": binding,
        "enable-in-lockscreen": False,
    }

    for key, desired_value in desired_values.items():
        current_value = shortcut_get(shortcut_path, key)

        if current_value == desired_value:
            continue

        if isinstance(desired_value, str):
            gsettings_set(
                BINDING_SCHEMA,
                key,
                gsettings_string(desired_value),
                shortcut_path,
            )
        elif isinstance(desired_value, bool):
            gsettings_set(
                BINDING_SCHEMA,
                key,
                gsettings_bool(desired_value),
                shortcut_path,
            )
        else:
            raise RuntimeError(f"Unsupported value type for {key}")

        changed = True

    return {
        "changed": changed,
        "path": shortcut_path,
        "name": name,
        "command": command,
        "binding": binding,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Ensure GNOME has a custom shortcut for Any Key."
    )

    parser.add_argument("--name", required=True)
    parser.add_argument("--command", required=True)
    parser.add_argument("--binding", required=True)
    parser.add_argument(
        "--legacy-command",
        action="append",
        default=[],
        dest="legacy_commands",
    )

    args = parser.parse_args()

    try:
        result = ensure_shortcut(
            name=args.name,
            command=args.command,
            binding=args.binding,
            legacy_commands=args.legacy_commands,
        )
    except Exception as error:
        print(json.dumps({"changed": False, "failed": True, "error": str(error)}))
        return 1

    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())

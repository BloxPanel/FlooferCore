import inspect
import json
from datetime import datetime, timezone
from pathlib import Path

from twitchio.ext import commands

from components.general import GeneralCommands
from components.moderation import ModerationCommands
from components.stream import StreamCommands


# ============================================================
# OUTPUT
# ============================================================

OUTPUT_FILE = Path("website/commands.json")


# ============================================================
# COMPONENTS TO SCAN
# ============================================================
#
# Add future components here as we build them.
#
# Example:
#
# from components.moderation import ModerationCommands
# from components.quotes import QuoteCommands
#
# COMPONENTS = [
#     GeneralCommands,
#     ModerationCommands,
#     QuoteCommands,
# ]
#

COMPONENTS = [
    GeneralCommands,
    ModerationCommands,
    StreamCommands,
]


# ============================================================
# COMMAND EXTRACTION
# ============================================================

def extract_commands_from_component(component_class):
    found_commands = []

    for _, member in inspect.getmembers(component_class):

        # We only care about TwitchIO Command objects.
        if not isinstance(member, commands.Command):
            continue

        callback = member.callback

        # This is the metadata we attached using @site_command(...)
        metadata = getattr(
            callback,
            "__site_command__",
            None,
        )

        # If a command doesn't have website metadata,
        # don't publish it to the command website.
        if metadata is None:
            continue

        aliases = list(member.aliases or [])

        usage = metadata.get("usage")

        # If we don't explicitly provide usage,
        # build it automatically from TwitchIO's signature.
        if not usage:
            signature = member.signature

            if signature:
                usage = f"!{member.name} {signature}"
            else:
                usage = f"!{member.name}"

        command_data = {
            "name": member.name,
            "aliases": aliases,
            "description": metadata.get(
                "description",
                "No description available.",
            ),
            "category": metadata.get(
                "category",
                "Other",
            ),
            "permission": metadata.get(
                "permission",
                "Everyone",
            ),
            "usage": usage,
        }

        found_commands.append(command_data)

    return found_commands


# ============================================================
# GENERATOR
# ============================================================

def generate_commands():
    commands_list = []

    for component_class in COMPONENTS:

        component_commands = extract_commands_from_component(
            component_class
        )

        commands_list.extend(
            component_commands
        )

    # --------------------------------------------------------
    # Sort commands
    # --------------------------------------------------------

    commands_list.sort(
        key=lambda command: (
            command["category"].lower(),
            command["name"].lower(),
        )
    )

    # --------------------------------------------------------
    # Build JSON payload
    # --------------------------------------------------------

    payload = {
        "updated_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "commands": commands_list,
    }

    # --------------------------------------------------------
    # Ensure website folder exists
    # --------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Write JSON
    # --------------------------------------------------------

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            payload,
            file,
            indent=4,
            ensure_ascii=False,
        )

        file.write("\n")

    # --------------------------------------------------------
    # Console output
    # --------------------------------------------------------

    print("=" * 60)
    print("FlooferCore command website generator")
    print("=" * 60)

    print(
        f"Generated {len(commands_list)} command(s)"
    )

    print(
        f"Output: {OUTPUT_FILE}"
    )

    print()

    for command in commands_list:

        aliases = command["aliases"]

        if aliases:
            alias_text = (
                " | aliases: "
                + ", ".join(
                    f"!{alias}"
                    for alias in aliases
                )
            )
        else:
            alias_text = ""

        print(
            f"[{command['category']}] "
            f"!{command['name']}"
            f"{alias_text}"
        )

    print("=" * 60)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    generate_commands()
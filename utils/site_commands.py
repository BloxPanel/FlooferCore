from typing import Callable


def site_command(
    *,
    description: str,
    category: str,
    permission: str = "Everyone",
    usage: str | None = None,
):
    """
    Attach website metadata to a Twitch command.

    This does not change how TwitchIO handles the command.
    It only gives our website generator information about it.
    """

    def decorator(func: Callable) -> Callable:
        func.__site_command__ = {
            "description": description,
            "category": category,
            "permission": permission,
            "usage": usage,
        }

        return func

    return decorator
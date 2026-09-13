from twitchio.ext import commands


def is_broadcaster(ctx: commands.Context) -> bool:
    """
    Returns True if the command author is the channel broadcaster.
    """

    return (
        str(ctx.chatter.id)
        == str(ctx.broadcaster.id)
    )


def is_moderator(ctx: commands.Context) -> bool:
    """
    Returns True if the command author is a moderator
    or the broadcaster.
    """

    if is_broadcaster(ctx):
        return True

    return bool(
        getattr(
            ctx.chatter,
            "moderator",
            False,
        )
    )


def is_vip(ctx: commands.Context) -> bool:
    """
    Returns True if the command author is a VIP,
    moderator, or broadcaster.
    """

    if is_moderator(ctx):
        return True

    return bool(
        getattr(
            ctx.chatter,
            "vip",
            False,
        )
    )


def is_subscriber(ctx: commands.Context) -> bool:
    """
    Returns True if the command author is a subscriber.
    """

    return bool(
        getattr(
            ctx.chatter,
            "subscriber",
            False,
        )
    )
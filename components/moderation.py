from twitchio.ext import commands

from utils.permissions import (
    is_broadcaster,
    is_moderator,
)
from utils.site_commands import site_command

def parse_duration(value: str) -> int:
    value = value.strip().lower()

    if value.isdigit():
        return int(value)

    unit = value[-1]
    number = value[:-1]

    if not number.isdigit():
        raise ValueError("Invalid duration format")

    amount = int(number)

    multipliers = {
        "s": 1,
        "m": 60,
        "h": 3600,
        "d": 86400,
    }

    if unit not in multipliers:
        raise ValueError("Invalid duration unit")

    return amount * multipliers[unit]

class ModerationCommands(commands.Component):
    def __init__(self, bot):
        self.bot = bot

    # ========================================================
    # MOD TEST
    # ========================================================

    @commands.command(name="modtest")
    @site_command(
        description="Checks whether FlooferCore recognizes you as a moderator.",
        category="Moderation",
        permission="Moderators",
        usage="!modtest",
    )
    async def modtest(
        self,
        ctx: commands.Context,
    ) -> None:

        if not is_moderator(ctx):
            await ctx.send(
                f"@{ctx.chatter.display_name}, "
                "this command is for moderators."
            )
            return

        if is_broadcaster(ctx):
            await ctx.send(
                f"@{ctx.chatter.display_name}, "
                "broadcaster permissions confirmed."
            )
            return

        await ctx.send(
            f"@{ctx.chatter.display_name}, "
            "moderator permissions confirmed."
        )

    # ========================================================
    # TIMEOUT
    # ========================================================

    @commands.command(
        name="timeout",
        aliases=["to", "mute"],
    )
    @site_command(
        description="Times a user out from chat.",
        category="Moderation",
        permission="Moderators",
        usage="!timeout <username> <duration (s, m, h, d)> [reason]",
    )
    async def timeout(
        self,
        ctx: commands.Context,
        username: str | None = None,
        duration: str | None = None,
        *,
        reason: str | None = None,
    ) -> None:

        # ----------------------------------------------------
        # PERMISSION CHECK
        # ----------------------------------------------------

        if not is_moderator(ctx):
            return

        # ----------------------------------------------------
        # ARGUMENT CHECK
        # ----------------------------------------------------

        if username is None or duration is None:
            await ctx.send(
                f"@{ctx.chatter.display_name}, usage: "
                "!timeout <username> <seconds> [reason]"
            )
            return

        # Allow @username as well as username
        username = username.lstrip("@")

        # ----------------------------------------------------
        # DURATION
        # ----------------------------------------------------

        try:
            duration_seconds = parse_duration(duration)

        except ValueError:
            await ctx.send(
                f"@{ctx.chatter.display_name}, "
                    "timeout duration must be a number of seconds."
            )
            return

        # Twitch limits timeouts to:
        # 1 second -> 1,209,600 seconds (2 weeks)

        if not 1 <= duration_seconds <= 1_209_600:
            await ctx.send(
                f"@{ctx.chatter.display_name}, "
                "timeout duration must be between "
                "1 second and 2 weeks."
            )
            return

        # ----------------------------------------------------
        # RESOLVE USER
        # ----------------------------------------------------

        try:
            users = await self.bot.fetch_users(
                logins=[username]
            )

        except Exception as error:
            await ctx.send(
                f"@{ctx.chatter.display_name}, "
                "I couldn't look that user up."
            )

            print(
                "[MODERATION] Failed to resolve "
                f"{username}: {error}"
            )

            return

        if not users:
            await ctx.send(
                f"@{ctx.chatter.display_name}, "
                f"I couldn't find Twitch user @{username}."
            )
            return

        target = users[0]

        # ----------------------------------------------------
        # SELF PROTECTION
        # ----------------------------------------------------

        if str(target.id) == str(ctx.chatter.id):
            await ctx.send(
                f"@{ctx.chatter.display_name}, "
                "you can't timeout yourself through FlooferCore."
            )
            return

        # ----------------------------------------------------
        # BOT PROTECTION
        # ----------------------------------------------------

        if str(target.id) == str(self.bot.bot_id):
            await ctx.send(
                f"@{ctx.chatter.display_name}, "
                "nice try. I'm not timing myself out."
            )
            return

        # ----------------------------------------------------
        # APPLY TIMEOUT
        # ----------------------------------------------------

        try:
            broadcaster = self.bot.create_partialuser(
                user_id=self.bot.owner_id
            )

            await broadcaster.timeout_user(
                moderator=self.bot.bot_id,
                user=target.id,
                duration=duration_seconds,
                reason=reason,
                token_for=self.bot.bot_id,
            )

        except Exception as error:
            await ctx.send(
                f"@{ctx.chatter.display_name}, "
                f"I couldn't timeout @{target.display_name}."
            )

            print(
                "[MODERATION] Timeout failed | "
                f"Moderator: {ctx.chatter.name} "
                f"({ctx.chatter.id}) | "
                f"Target: {target.name} "
                f"({target.id}) | "
                f"Duration: {duration_seconds} | "
                f"Reason: {reason!r} | "
                f"Error: {error}"
            )

            return

        # ----------------------------------------------------
        # LOG SUCCESS
        # ----------------------------------------------------

        print(
            "[MODERATION] Timeout successful | "
            f"Moderator: {ctx.chatter.name} "
            f"({ctx.chatter.id}) | "
            f"Target: {target.name} "
            f"({target.id}) | "
            f"Duration: {duration_seconds}s | "
            f"Reason: {reason!r}"
        )

        # Intentionally no success message in Twitch chat.
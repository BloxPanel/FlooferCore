from twitchio.ext import commands

from utils.durations import parse_duration
from utils.permissions import (
    is_broadcaster,
    is_moderator,
)
from utils.site_commands import site_command


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
        usage="!timeout <username> <duration> [reason]",
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
                "!timeout <username> <duration> [reason] "
                "(examples: 60s, 5m, 2h, 1d)"
            )
            return

        username = username.lstrip("@")

        # ----------------------------------------------------
        # DURATION
        # ----------------------------------------------------

        try:
            duration_seconds = parse_duration(duration)

        except ValueError:
            await ctx.send(
                f"@{ctx.chatter.display_name}, "
                "invalid timeout duration. Use formats like "
                "60s, 5m, 2h, or 1d."
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

        # Intentionally silent in Twitch chat.

    # ========================================================
    # BAN
    # ========================================================

    @commands.command(
        name="ban",
    )
    @site_command(
        description="Permanently bans a user from chat.",
        category="Moderation",
        permission="Moderators",
        usage="!ban <username> [reason]",
    )
    async def ban(
        self,
        ctx: commands.Context,
        username: str | None = None,
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

        if username is None:
            await ctx.send(
                f"@{ctx.chatter.display_name}, usage: "
                "!ban <username> [reason]"
            )
            return

        username = username.lstrip("@")

        # ----------------------------------------------------
        # REASON LENGTH
        # ----------------------------------------------------

        if reason and len(reason) > 500:
            await ctx.send(
                f"@{ctx.chatter.display_name}, "
                "ban reasons cannot exceed 500 characters."
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
                "you can't ban yourself through FlooferCore."
            )
            return

        # ----------------------------------------------------
        # BOT PROTECTION
        # ----------------------------------------------------

        if str(target.id) == str(self.bot.bot_id):
            await ctx.send(
                f"@{ctx.chatter.display_name}, "
                "nice try."
            )
            return

        # ----------------------------------------------------
        # APPLY BAN
        # ----------------------------------------------------

        try:
            broadcaster = self.bot.create_partialuser(
                user_id=self.bot.owner_id
            )

            await broadcaster.ban_user(
                moderator=self.bot.bot_id,
                user=target.id,
                reason=reason,
                token_for=self.bot.bot_id,
            )

        except Exception as error:
            await ctx.send(
                f"@{ctx.chatter.display_name}, "
                f"I couldn't ban @{target.display_name}."
            )

            print(
                "[MODERATION] Ban failed | "
                f"Moderator: {ctx.chatter.name} "
                f"({ctx.chatter.id}) | "
                f"Target: {target.name} "
                f"({target.id}) | "
                f"Reason: {reason!r} | "
                f"Error: {error}"
            )

            return

        # ----------------------------------------------------
        # LOG SUCCESS
        # ----------------------------------------------------

        print(
            "[MODERATION] Ban successful | "
            f"Moderator: {ctx.chatter.name} "
            f"({ctx.chatter.id}) | "
            f"Target: {target.name} "
            f"({target.id}) | "
            f"Reason: {reason!r}"
        )

        # Intentionally silent in Twitch chat.

    # ========================================================
    # UNBAN
    # ========================================================

    @commands.command(
        name="unban",
        aliases=["untimeout"],
    )
    @site_command(
        description="Removes a user's ban or timeout.",
        category="Moderation",
        permission="Moderators",
        usage="!unban <username>",
    )
    async def unban(
        self,
        ctx: commands.Context,
        username: str | None = None,
    ) -> None:

        # ----------------------------------------------------
        # PERMISSION CHECK
        # ----------------------------------------------------

        if not is_moderator(ctx):
            return

        # ----------------------------------------------------
        # ARGUMENT CHECK
        # ----------------------------------------------------

        if username is None:
            await ctx.send(
                f"@{ctx.chatter.display_name}, usage: "
                "!unban <username>"
            )
            return

        username = username.lstrip("@")

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
        # REMOVE BAN / TIMEOUT
        # ----------------------------------------------------

        try:
            broadcaster = self.bot.create_partialuser(
                user_id=self.bot.owner_id
            )

            await broadcaster.unban_user(
                moderator=self.bot.bot_id,
                user_id=target.id,
                token_for=self.bot.bot_id,
            )

        except Exception as error:
            await ctx.send(
                f"@{ctx.chatter.display_name}, "
                f"I couldn't unban @{target.display_name}."
            )

            print(
                "[MODERATION] Unban failed | "
                f"Moderator: {ctx.chatter.name} "
                f"({ctx.chatter.id}) | "
                f"Target: {target.name} "
                f"({target.id}) | "
                f"Error: {error}"
            )

            return

        # ----------------------------------------------------
        # LOG SUCCESS
        # ----------------------------------------------------

        print(
            "[MODERATION] Unban successful | "
            f"Moderator: {ctx.chatter.name} "
            f"({ctx.chatter.id}) | "
            f"Target: {target.name} "
            f"({target.id})"
        )

        # Intentionally silent in Twitch chat.

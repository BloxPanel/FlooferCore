from datetime import datetime, timezone

from twitchio.ext import commands

from utils.site_commands import site_command


class StreamCommands(commands.Component):
    def __init__(self, bot):
        self.bot = bot

    # ========================================================
    # STREAM UPTIME
    # ========================================================

    @commands.command(
        name="uptime",
        aliases=["live"],
    )
    @site_command(
        description="Shows how long the current stream has been live.",
        category="Stream",
        permission="Everyone",
        usage="!uptime",
    )
    async def uptime(
        self,
        ctx: commands.Context,
    ) -> None:

        # ----------------------------------------------------
        # FETCH CURRENT STREAM
        # ----------------------------------------------------

        try:
            streams = await self.bot.fetch_streams(
                user_ids=[
                    self.bot.owner_id
                ],
                first=1,
            )

        except Exception as error:
            await ctx.send(
                "I couldn't check the stream status right now."
            )

            print(
                "[STREAM] Failed to fetch stream status | "
                f"Error: {error}"
            )

            return

        # ----------------------------------------------------
        # OFFLINE
        # ----------------------------------------------------

        if not streams:
            await ctx.send(
                "silasdafloofer is currently offline."
            )
            return

        stream = streams[0]

        # ----------------------------------------------------
        # CALCULATE UPTIME
        # ----------------------------------------------------

        started_at = stream.started_at

        now = datetime.now(
            timezone.utc
        )

        elapsed = now - started_at

        total_seconds = int(
            elapsed.total_seconds()
        )

        days, remainder = divmod(
            total_seconds,
            86400,
        )

        hours, remainder = divmod(
            remainder,
            3600,
        )

        minutes, _ = divmod(
            remainder,
            60,
        )

        # ----------------------------------------------------
        # FORMAT
        # ----------------------------------------------------

        parts = []

        if days:
            parts.append(
                f"{days}d"
            )

        if hours:
            parts.append(
                f"{hours}h"
            )

        if minutes:
            parts.append(
                f"{minutes}m"
            )

        if not parts:
            parts.append(
                "<1m"
            )

        uptime_text = " ".join(
            parts
        )

        # ----------------------------------------------------
        # RESPONSE
        # ----------------------------------------------------

        await ctx.send(
            f"silasdafloofer has been live for "
            f"{uptime_text}."
        )
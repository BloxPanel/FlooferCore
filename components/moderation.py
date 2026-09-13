from twitchio.ext import commands

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
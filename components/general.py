import time

from twitchio.ext import commands


class GeneralCommands(commands.Component):
    def __init__(self, bot):
        self.bot = bot

    # ========================================================
    # PING
    # ========================================================

    @commands.command(name="ping")
    async def ping(self, ctx: commands.Context) -> None:
        """
        Basic test command to make sure FlooferCore is alive.
        """

        await ctx.send("Pong!")

    # ========================================================
    # HELLO
    # ========================================================

    @commands.command(name="hello", aliases=["hi"])
    async def hello(self, ctx: commands.Context) -> None:
        """
        Say hello to whoever used the command.
        """

        await ctx.send(
            f"Hello, {ctx.chatter.display_name}! 👋"
        )

    # ========================================================
    # UPTIME
    # ========================================================

    @commands.command(name="uptime")
    async def uptime(self, ctx: commands.Context) -> None:
        """
        Shows how long FlooferCore itself has been running.
        """

        elapsed = time.monotonic() - self.bot.started_at

        hours, remainder = divmod(int(elapsed), 3600)
        minutes, seconds = divmod(remainder, 60)

        if hours > 0:
            uptime_text = f"{hours}h {minutes}m {seconds}s"

        elif minutes > 0:
            uptime_text = f"{minutes}m {seconds}s"

        else:
            uptime_text = f"{seconds}s"

        await ctx.send(
            f"FlooferCore has been online for {uptime_text}."
        )

    # ========================================================
    # COMMANDS
    # ========================================================

    @commands.command(name="commands", aliases=["help"])
    async def commands_list(self, ctx: commands.Context) -> None:
        """
        Displays the basic FlooferCore commands.
        """

        await ctx.send(
            "Commands: !ping | !hello | !uptime | !commands"
        )
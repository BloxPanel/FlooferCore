import time

from twitchio.ext import commands

from utils.site_commands import site_command


class GeneralCommands(commands.Component):
    def __init__(self, bot):
        self.bot = bot

    # ========================================================
    # PING
    # ========================================================

    @commands.command(name="ping")
    @site_command(
        description="Checks whether FlooferCore is online and responding.",
        category="General",
        permission="Everyone",
        usage="!ping",
    )
    async def ping(self, ctx: commands.Context) -> None:
        """
        Basic test command to make sure FlooferCore is alive.
        """

        await ctx.send("Pong!")

    # ========================================================
    # HELLO
    # ========================================================

    @commands.command(
        name="hello",
        aliases=["hi"],
    )
    @site_command(
        description="FlooferCore says hello to you.",
        category="General",
        permission="Everyone",
        usage="!hello",
    )
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

    @commands.command(name="runtime", aliases=["up"])
    @site_command(
        description="Shows how long FlooferCore has been running.",
        category="General",
        permission="Everyone",
        usage="!runtime",
    )
    async def uptime(self, ctx: commands.Context) -> None:
        """
        Shows how long FlooferCore itself has been running.
        """

        elapsed = (
            time.monotonic()
            - self.bot.started_at
        )

        hours, remainder = divmod(
            int(elapsed),
            3600,
        )

        minutes, seconds = divmod(
            remainder,
            60,
        )

        if hours > 0:
            uptime_text = (
                f"{hours}h "
                f"{minutes}m "
                f"{seconds}s"
            )

        elif minutes > 0:
            uptime_text = (
                f"{minutes}m "
                f"{seconds}s"
            )

        else:
            uptime_text = (
                f"{seconds}s"
            )

        await ctx.send(
            f"FlooferCore has been online for "
            f"{uptime_text}."
        )

    # ========================================================
    # COMMANDS
    # ========================================================

    @commands.command(
        name="commands",
        aliases=["help"],
    )
    @site_command(
        description="Shows the available FlooferCore commands.",
        category="General",
        permission="Everyone",
        usage="!commands",
    )
    async def commands_list(
        self,
        ctx: commands.Context,
    ) -> None:
        """
        Displays the FlooferCore command website.
        """

        await ctx.send(
            "Commands: "
            "https://floofercommands.builtbybuzz.dev"
        )

    @commands.command(
        name="discord",
        aliases=["server"],
    )
    @site_command(
        description="pastes the discord invite for Silas's Discord server.",
        category="General",
        permission="Everyone",
        usage="!discord",
    )
    async def discord(
        self,
        ctx: commands.Context,
    ) -> None:
        """
        Displays the Discord invite for Silas's Discord server.
        """

        await ctx.send(
            "Join the Discord server: "
            "https://discord.gg/QwJJ2M877z"
        )

    @commands.command(
        name="lurk"
    )
    @site_command(
        description="Lets the streamer know you're lurking.",
        category="General",
        permission="Everyone",
        usage="!lurk",
    )
    async def lurk(
        self,
        ctx: commands.Context,
    ) -> None:
        await ctx.send(
            f"{ctx.chatter.display_name} has fallen into the fluffy realms of VRChat and is now lurking."
        )

    @commands.command(
        name="gay"
    )
    @site_command(
        description="Shows a percentage of the gayness for the user",
        category="General",
        permission="Everyone",
        usage="!gay",
    )
    async def gay(
        self,
        ctx: commands.Context,
    ):
        """
        Displays a random percentage of gayness for the user.
        """

        import random

        percentage = random.randint(0, 100)

        if ctx.chatter.display_name.lower() == "silasdafloofer":
            msg = f"{ctx.chatter.display_name} is 150% gay!"
        else:
            msg = f"{ctx.chatter.display_name} is {percentage}% gay!"

        await ctx.send(
            msg
        )
    
    @commands.command(
        name="zesty"
    )
    @site_command(
        description="Shows a percentage of the zestiness for the user",
        category="General",
        permission="Everyone",
        usage="!zesty",
    )
    async def zesty(
        self,
        ctx: commands.Context,
    ):
        """
        Displays a random percentage of zestiness for the user.
        """

        import random

        percentage = random.randint(0, 100)

        if ctx.chatter.display_name.lower() == "silasdafloofer":
            msg = f"{ctx.chatter.display_name} is 150% zesty!"
        else:
            msg = f"{ctx.chatter.display_name} is {percentage}% zesty!"
        
        await ctx.send(
            msg
        )

    @commands.command(
        name="floofgay",
    )
    async def floofgay(self, ctx: commands.Context) -> None:
        await ctx.send(
            f"@silasdafloofer is 150% gay!"
        )
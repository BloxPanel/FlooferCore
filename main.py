import asyncio
import logging
import os
import time

import twitchio
from twitchio import eventsub
from twitchio.ext import commands
from dotenv import load_dotenv

from components.general import GeneralCommands


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")

ACCESS_TOKEN = os.getenv("TWITCH_ACCESS_TOKEN")
REFRESH_TOKEN = os.getenv("TWITCH_REFRESH_TOKEN")

BOT_ID = os.getenv("TWITCH_BOT_ID")
CHANNEL_ID = os.getenv("TWITCH_CHANNEL_ID")


required_values = {
    "TWITCH_CLIENT_ID": CLIENT_ID,
    "TWITCH_CLIENT_SECRET": CLIENT_SECRET,
    "TWITCH_ACCESS_TOKEN": ACCESS_TOKEN,
    "TWITCH_REFRESH_TOKEN": REFRESH_TOKEN,
    "TWITCH_BOT_ID": BOT_ID,
    "TWITCH_CHANNEL_ID": CHANNEL_ID,
}

for name, value in required_values.items():
    if not value:
        raise RuntimeError(
            f"{name} is missing from .env"
        )


# ============================================================
# LOGGING
# ============================================================

LOGGER = logging.getLogger("FlooferCore")


# ============================================================
# BOT
# ============================================================

class FlooferCore(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            bot_id=BOT_ID,
            owner_id=CHANNEL_ID,
            prefix="!",
        )

        # Used by !uptime.
        self.started_at = time.monotonic()

    # ========================================================
    # SETUP
    # ========================================================

    async def setup_hook(self) -> None:
        LOGGER.info("Running FlooferCore setup...")

        # ----------------------------------------------------
        # OAuth token
        # ----------------------------------------------------

        validation = await self.add_token(
            ACCESS_TOKEN,
            REFRESH_TOKEN,
        )

        LOGGER.info(
            "Loaded Twitch token for user ID %s",
            validation.user_id,
        )

        # ----------------------------------------------------
        # Components
        # ----------------------------------------------------

        await self.add_component(
            GeneralCommands(self)
        )

        LOGGER.info(
            "Loaded component: GeneralCommands"
        )

        # ----------------------------------------------------
        # EventSub chat
        # ----------------------------------------------------

        subscription = eventsub.ChatMessageSubscription(
            broadcaster_user_id=CHANNEL_ID,
            user_id=BOT_ID,
        )

        await self.subscribe_websocket(
            payload=subscription,
            as_bot=True,
        )

        LOGGER.info(
            "Subscribed to chat messages for channel %s",
            CHANNEL_ID,
        )

    # ========================================================
    # READY
    # ========================================================

    async def event_ready(self) -> None:
        LOGGER.info("=" * 60)
        LOGGER.info("FlooferCore is ONLINE")
        LOGGER.info("Bot ID:     %s", BOT_ID)
        LOGGER.info("Channel ID: %s", CHANNEL_ID)
        LOGGER.info("=" * 60)

    # ========================================================
    # CHAT
    # ========================================================

    async def event_message(
        self,
        payload: twitchio.ChatMessage,
    ) -> None:

        LOGGER.info(
            "[CHAT] %s: %s",
            payload.chatter.name,
            payload.text,
        )

        await self.process_commands(payload)

    # ========================================================
    # COMMAND ERROR HANDLER
    # ========================================================

    async def event_command_error(
        self,
        payload: commands.CommandErrorPayload,
    ) -> None:

        error = payload.exception
        ctx = payload.context

        # ----------------------------------------------------
        # Unknown command
        # ----------------------------------------------------
        #
        # Someone saying:
        #
        # !asdfghjkl
        #
        # should NOT dump a giant traceback into our console.
        # Just quietly ignore it.

        if isinstance(error, commands.CommandNotFound):
            LOGGER.debug(
                "Unknown command from %s: %s",
                ctx.chatter.name,
                ctx.content,
            )

            return

        # ----------------------------------------------------
        # Actual command failure
        # ----------------------------------------------------
        #
        # These ARE important, so log them properly.

        LOGGER.error(
            "Error while processing command from %s: %s",
            ctx.chatter.name,
            error,
            exc_info=error,
        )


# ============================================================
# RUNNER
# ============================================================

async def runner() -> None:
    async with FlooferCore() as bot:
        await bot.start(
            load_tokens=False
        )


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    twitchio.utils.setup_logging(
        level=logging.INFO
    )

    try:
        asyncio.run(runner())

    except KeyboardInterrupt:
        LOGGER.info(
            "FlooferCore shutting down."
        )


if __name__ == "__main__":
    main()
import asyncio
import os

import twitchio
from dotenv import load_dotenv


load_dotenv()

CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")


if not CLIENT_ID:
    raise RuntimeError("TWITCH_CLIENT_ID is missing from .env")

if not CLIENT_SECRET:
    raise RuntimeError("TWITCH_CLIENT_SECRET is missing from .env")


async def main():
    client = twitchio.Client(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    )

    async with client:
        # Generate an App Access Token using our Client ID + Secret.
        await client.login()

        users = await client.fetch_users(
            logins=[
                "FlooferCore",
                "silasdafloofer",
            ]
        )

        for user in users:
            print(f"{user.name}: {user.id}")


if __name__ == "__main__":
    asyncio.run(main())
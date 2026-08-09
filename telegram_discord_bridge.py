import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any

import discord
from telethon import TelegramClient, events
from telethon.tl.types import MessageService


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        logging.warning("State file is unreadable, starting with empty state")
        return {}


def save_state(path: Path, state: dict[str, Any]) -> None:
    path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")


def build_discord_message(channel_name: str, message_id: int, text: str, link: str | None) -> str:
    clean_text = text.strip() if text else "[Media post or empty text]"
    if len(clean_text) > 1500:
        clean_text = clean_text[:1497] + "..."

    lines = [
        f"**New Telegram post in {channel_name}**",
        f"`message_id`: {message_id}",
        clean_text,
    ]

    if link:
        lines.append(link)

    message = "\n".join(lines)
    if len(message) > 1990:
        message = message[:1987] + "..."
    return message


class BridgeDiscordClient(discord.Client):
    def __init__(self) -> None:
        intents = discord.Intents.none()
        super().__init__(intents=intents)
        self.ready_event = asyncio.Event()

    async def on_ready(self) -> None:
        logging.info("Discord bot logged in as %s", self.user)
        self.ready_event.set()


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    tg_api_id = int(require_env("TG_API_ID"))
    tg_api_hash = require_env("TG_API_HASH")
    tg_channel_ref = require_env("TG_CHANNEL")

    discord_token = require_env("DISCORD_BOT_TOKEN")
    discord_channel_id = int(require_env("DISCORD_CHANNEL_ID"))

    tg_session = os.getenv("TG_SESSION", "tg_bridge_session")
    state_file = Path(os.getenv("STATE_FILE", "bridge_state.json"))
    state = load_state(state_file)

    discord_client = BridgeDiscordClient()
    discord_task = asyncio.create_task(discord_client.start(discord_token))

    try:
        await asyncio.wait_for(discord_client.ready_event.wait(), timeout=60)
        discord_channel = discord_client.get_channel(discord_channel_id)
        if discord_channel is None:
            discord_channel = await discord_client.fetch_channel(discord_channel_id)

        if not hasattr(discord_channel, "send"):
            raise RuntimeError("Configured DISCORD_CHANNEL_ID is not a sendable channel")

        tg_client = TelegramClient(tg_session, tg_api_id, tg_api_hash)
        await tg_client.start()

        entity = await tg_client.get_entity(tg_channel_ref)
        channel_id_key = str(getattr(entity, "id", tg_channel_ref))
        channel_title = getattr(entity, "title", tg_channel_ref)
        channel_username = getattr(entity, "username", None)

        last_seen_id = int(state.get(channel_id_key, 0))
        logging.info("Monitoring Telegram channel: %s (last_seen_id=%s)", channel_title, last_seen_id)

        @tg_client.on(events.NewMessage(chats=entity))
        async def on_new_message(event: events.NewMessage.Event) -> None:
            nonlocal last_seen_id

            msg = event.message
            if msg is None or isinstance(msg, MessageService):
                return

            if msg.id <= last_seen_id:
                return

            public_link = None
            if channel_username:
                public_link = f"https://t.me/{channel_username}/{msg.id}"

            payload = build_discord_message(
                channel_name=channel_title,
                message_id=msg.id,
                text=msg.message or "",
                link=public_link,
            )

            await discord_channel.send(payload)

            last_seen_id = msg.id
            state[channel_id_key] = last_seen_id
            save_state(state_file, state)
            logging.info("Forwarded Telegram message id=%s", msg.id)

        await tg_client.run_until_disconnected()
    finally:
        await discord_client.close()
        if not discord_task.done():
            await discord_task


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bridge stopped")

# Telegram to Discord Bridge 💬➡️🤖

This is a Python script developed as a personal project to automatically forward new posts from a Telegram channel directly to a specified Discord channel in real time. To check when new episodes of project RED are released

## Description 📜

The script uses `telethon` and `discord.py` to establish a live bridge between Telegram and Discord. It monitors a target Telegram channel for new messages, formats the post content, and sends it to a designated Discord channel while tracking the last forwarded message ID in a local state file to prevent duplicate postings upon restart. The script performs the following operations:

1. **Client Initialization & State Loading:** Connects to Discord using a bot token and connects to Telegram via Telethon (supporting StringSessions for headless environments or local session files). It loads `bridge_state.json` to keep track of the last forwarded `message_id`.


2. **Message Monitoring & Formatting:** Listens for new incoming posts from the target Telegram channel. Automatically cleans text formatting, handles empty or media-only post placeholders, and appends direct public Telegram post links when available.


3. **Chunking & Discord Forwarding:** Ensures messages adhere to Discord's 2000-character limit by automatically splitting long posts into clean chunks before posting. Updates and saves the state file after each successful message transfer.



## How to use 🚀

1. **Prerequisites:** Make sure you have Python installed on your system or VPS. Install all required dependencies using the `requirements.txt` file included in the repository:


```bash
pip install -r requirements.txt

```


2. **Environment Variables Configuration:** Configure the required environment variables on your system, VPS environment, or `.env` file before executing the script:


```bash
export TG_API_ID="your_telegram_api_id"
export TG_API_HASH="your_telegram_api_hash"
export TG_CHANNEL="your_telegram_channel_username_or_id"
export DISCORD_BOT_TOKEN="your_discord_bot_token"
export DISCORD_CHANNEL_ID="your_discord_channel_id"

```


(Optional variables: `TG_SESSION_STRING` for Telethon StringSession authentication on headless servers, or `STATE_FILE` to customize the state filename).


3. **Navigate to the script directory:** Open the command line or terminal and navigate to the directory where the repository is located. For example:
```bash
cd tg-discord-bridge

```


4. **Script Execution:** Once configured, start the bridge script:
```bash
python bridge.py

```


*(Note: Replace `bridge.py` with the actual filename of your script).*
5. **VPS Deployment:** For continuous 24/7 background operation on a VPS, you can run the process using a process manager such as `pm2`, `tmux`, `screen`, or a custom `systemd` service.



## License 📄

This project is licensed under the [MIT License](https://www.google.com/search?q=LICENSE).

Made with ❤️ by Texdroid

# Reddit to Telegram Bot

This repository contains a simple Python script that fetches the top posts from a subreddit and forwards them to a Telegram channel. Posts are "translated" using a small stub that prepends some Russian text and a smiley.

## Usage

1. Copy `.env.example` to `.env` and fill in:
   - `TELEGRAM_BOT_TOKEN` – token for your Telegram bot.
   - `TELEGRAM_CHAT_ID` – ID of the target channel or chat.
   - `SUBREDDIT` – subreddit to parse (default: `python`).

2. **Run the script**:

```bash
python reddit_to_telegram.py
```

The script uses the Telegram Bot API and Reddit's public JSON feeds. Internet access is required when running it in a real environment.

## Testing

Unit tests can be executed with:

```bash
pytest -q
```

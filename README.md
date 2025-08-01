# Reddit to Telegram Bot

This repository contains a tiny Telegram bot. Send it a Reddit post URL and it
will fetch the post, grab the first image or video, "translate" the title into
Russian and publish the result to a Telegram channel. Translation is only a
stub and simply prepends some text.

## Usage

1. Copy `.env.example` to `.env` and fill in:
   - `TELEGRAM_BOT_TOKEN` – token for your Telegram bot.
   - `TELEGRAM_CHAT_ID` – ID of the channel where posts should be published.

2. **Run the script**:

```bash
python reddit_to_telegram.py
```

The script uses the Telegram Bot API and Reddit's public JSON feeds. Internet
access is required when running it in a real environment.

## Testing

Unit tests can be executed with:

```bash
pytest -q
```

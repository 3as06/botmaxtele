"""Tiny Reddit to Telegram relay.

The bot expects a Reddit post URL in a private chat. It fetches the post,
grabs the first available image or video and "translates" the title into
Russian using a very small stub. The result is published to a configured
channel.

Network access is required when running the bot for real. All network
interactions can be mocked in unit tests.
"""

from __future__ import annotations

import json
import logging
import os
import re
import urllib.parse
import urllib.request
from typing import Dict, Optional


def load_env(path: str = ".env") -> None:
    """Load environment variables from a simple ``.env`` file if present."""

    if not os.path.exists(path):
        return

    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key, value)


def fetch_post_info(url: str) -> Dict[str, Optional[str]]:
    """Fetch information about a single Reddit post.

    Parameters
    ----------
    url:
        Direct link to a Reddit submission.

    Returns
    -------
    dict
        Dictionary with ``title``, ``selftext`` (may be empty), ``media_url``
        (URL to image or video) and ``media_type`` (``photo`` or ``video``).
    """

    api_url = url.rstrip("/") + ".json"
    req = urllib.request.Request(api_url, headers={"User-Agent": "telegram-bot/0.1"})
    with urllib.request.urlopen(req) as resp:
        data = json.load(resp)

    post = data[0]["data"]["children"][0]["data"]
    title = post.get("title", "")
    selftext = post.get("selftext", "")

    media_url: Optional[str] = None
    media_type: Optional[str] = None

    if post.get("is_video") and post.get("secure_media"):
        video = post["secure_media"].get("reddit_video")
        if video and video.get("fallback_url"):
            media_url = video["fallback_url"]
            media_type = "video"
    else:
        url_overridden = post.get("url_overridden_by_dest")
        if url_overridden and re.search(r"\.(jpg|jpeg|png|gif)$", url_overridden, re.I):
            media_url = url_overridden
            media_type = "photo"
        elif post.get("preview"):
            images = post["preview"].get("images")
            if images:
                source = images[0].get("source")
                if source and source.get("url"):
                    media_url = source["url"].replace("&amp;", "&")
                    media_type = "photo"

    return {
        "title": title,
        "selftext": selftext,
        "media_url": media_url,
        "media_type": media_type,
    }


def translate_text(text: str) -> str:
    """Stubbed translation that marks the text as Russian."""

    return f"Перевод: {text}"


def send_media(token: str, chat_id: str, media_url: str, caption: str, media_type: str) -> None:
    """Send photo or video to Telegram."""

    if media_type == "video":
        method = "sendVideo"
        field = "video"
    else:
        method = "sendPhoto"
        field = "photo"

    url = f"https://api.telegram.org/bot{token}/{method}"
    data = urllib.parse.urlencode({"chat_id": chat_id, field: media_url, "caption": caption}).encode()
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req) as resp:
        if resp.status != 200:
            logging.error("Failed to send media: %s", resp.read())


def handle_update(token: str, chat_id: str, update: Dict[str, object]) -> None:
    """Process a single Telegram update."""

    message = update.get("message")
    if not isinstance(message, dict):
        return

    text = str(message.get("text", ""))
    match = re.search(r"https?://(?:www\.)?reddit\.com/\S+", text)
    if not match:
        return

    post = fetch_post_info(match.group(0))
    caption = translate_text(post["title"])
    if post["media_url"] and post["media_type"]:
        send_media(token, chat_id, post["media_url"], caption, post["media_type"])
    else:
        # Fallback to text message if no media was found
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        body = urllib.parse.urlencode({"chat_id": chat_id, "text": caption}).encode()
        req = urllib.request.Request(url, data=body)
        with urllib.request.urlopen(req) as resp:
            if resp.status != 200:
                logging.error("Failed to send message: %s", resp.read())


def poll_updates(token: str, chat_id: str) -> None:
    """Continuously poll Telegram for new messages."""

    offset = 0
    while True:
        url = f"https://api.telegram.org/bot{token}/getUpdates?timeout=30&offset={offset}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            data = json.load(resp)

        for update in data.get("result", []):
            offset = max(offset, update.get("update_id", 0) + 1)
            handle_update(token, chat_id, update)


def main() -> None:
    load_env()
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        raise SystemExit("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set")

    poll_updates(token, chat_id)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()


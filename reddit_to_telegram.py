import json
import logging
import os
import urllib.request
from typing import List, Dict


def load_env(path: str = ".env") -> None:
    """Load environment variables from a simple .env file if present."""
    if not os.path.exists(path):
        return
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key, value)


def fetch_top_posts(subreddit: str, limit: int = 5) -> List[Dict[str, str]]:
    """Fetch top posts from a subreddit."""
    url = f"https://www.reddit.com/r/{subreddit}/top/.json?sort=top&t=day&limit={limit}"
    req = urllib.request.Request(url, headers={"User-Agent": "telegram-bot/0.1"})
    with urllib.request.urlopen(req) as resp:
        data = json.load(resp)
    posts = []
    for child in data.get("data", {}).get("children", []):
        post_data = child.get("data", {})
        posts.append(
            {
                "title": post_data.get("title", ""),
                "url": f"https://reddit.com{post_data.get('permalink', '')}",
            }
        )
    return posts


def translate_text(text: str) -> str:
    """Return a playful "translation" with a bit of context."""
    return f"Вот что пишут: {text} - надеюсь, ничего не пошло не так! 😂"


def format_post(post: Dict[str, str]) -> str:
    translated = translate_text(post["title"])
    return f"{translated}\n{post['url']}"


def send_to_telegram(token: str, chat_id: str, text: str) -> None:
    """Send a message via the Telegram Bot API."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode(
        {
            "chat_id": chat_id,
            "text": text,
        }
    ).encode()
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req) as resp:
        if resp.status != 200:
            logging.error("Failed to send message: %s", resp.read())


def main() -> None:
    load_env()
    subreddit = os.environ.get("SUBREDDIT", "python")
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise SystemExit("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set")
    posts = fetch_top_posts(subreddit)
    for post in posts:
        text = format_post(post)
        send_to_telegram(token, chat_id, text)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from reddit_to_telegram import fetch_top_posts, format_post

SAMPLE_JSON = {
    "data": {
        "children": [
            {"data": {"title": "Hello World", "permalink": "/r/test/comments/1"}},
            {"data": {"title": "Second Post", "permalink": "/r/test/comments/2"}},
        ]
    }
}


class DummyResponse:
    def __init__(self, data):
        self._data = data
        self.status = 200

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        pass

    def read(self):
        return json.dumps(self._data).encode()

    def __iter__(self):
        return iter([])


def test_fetch_top_posts(monkeypatch):
    def fake_urlopen(req):
        return DummyResponse(SAMPLE_JSON)

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    posts = fetch_top_posts("test", limit=2)
    assert len(posts) == 2
    assert posts[0]["title"] == "Hello World"
    assert posts[0]["url"].endswith("/r/test/comments/1")


def test_format_post():
    post = {"title": "Hello", "url": "https://example.com"}
    text = format_post(post)
    assert "Вот что пишут" in text
    assert "https://example.com" in text

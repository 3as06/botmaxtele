import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reddit_to_telegram import fetch_post_info, translate_text


POST_JSON = [
    {
        "data": {
            "children": [
                {
                    "data": {
                        "title": "Cute cat",
                        "selftext": "",
                        "url_overridden_by_dest": "https://i.redd.it/cat.jpg",
                        "is_video": False,
                        "preview": {
                            "images": [
                                {"source": {"url": "https://i.redd.it/cat.jpg"}}
                            ]
                        },
                    }
                }
            ]
        }
    }
]


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


def test_fetch_post_info(monkeypatch):
    def fake_urlopen(req):
        return DummyResponse(POST_JSON)

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    post = fetch_post_info("https://reddit.com/r/test/comments/1")
    assert post["title"] == "Cute cat"
    assert post["media_url"].endswith("cat.jpg")
    assert post["media_type"] == "photo"


def test_translate_text():
    result = translate_text("Hello")
    assert "Перевод" in result

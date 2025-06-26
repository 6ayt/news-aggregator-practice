from fastapi.testclient import TestClient
import feedparser

from backend.app import app, news_store, sources_store, STUDENT_ID

client = TestClient(app)

def test_fetch_custom_feed(monkeypatch):
    # Очищуємо глобальні сховища перед тестом
    news_store.clear()
    sources_store.clear()
    # Додаємо власне RSS-джерело
    response = client.post(f"/sources/{STUDENT_ID}", json={"url": "http://test.com/rss"})
    assert response.status_code == 200
    assert "http://test.com/rss" in response.json()["sources"]

    # Заглушка для feedparser.parse, щоб не робити реальний запит
    class DummyFeed:
        entries = [{"title": "X", "link": "L", "published": "2025-04-28"}]

    monkeypatch.setattr(feedparser, "parse", lambda url: DummyFeed())

    # Виконуємо fetch для STUDENT_ID, має повернути, що знайдена 1 стаття
    r = client.post(f"/fetch/{STUDENT_ID}")
    assert r.status_code == 200
    assert r.json() == {"fetched": 1}

    # Перевірка, що новини збереглись у news_store
    assert STUDENT_ID in news_store
    assert len(news_store[STUDENT_ID]) == 1
    assert news_store[STUDENT_ID][0]["title"] == "X"

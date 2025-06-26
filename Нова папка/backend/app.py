from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager
from config import STUDENT_ID, SOURCES
import config
import feedparser
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Сховища
news_store = {STUDENT_ID: []}
sources_store = {}
store = {STUDENT_ID: SOURCES.copy()}
analyzer = SentimentIntensityAnalyzer()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Lifespan події
@asynccontextmanager
async def lifespan(*_):
    student_id = getattr(config, "STUDENT_ID", None)
    sources = getattr(config, "SOURCES", [])
    if student_id and isinstance(sources, list):
        sources_store[student_id] = list(sources)
        print(f"[lifespan] loaded {len(sources)} feeds for {student_id}")
    yield

# Ініціалізація FastAPI
app = FastAPI(lifespan=lifespan)

# CORS
origins = [
    "http://localhost:8001/frontend/",
    "http://localhost:8001",
    "http://127.0.0.1:8001",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Фейкова БД користувача
fake_users_db = {
    STUDENT_ID: {
        "username": STUDENT_ID,
        "password": "password123",
        "full_name": "Віталій Бойко",
        "hashed_password": "fakehashedpassword123",
        "disabled": False,
    }
}

@app.get("/info")
def get_info():
    return {"student_id": STUDENT_ID}

@app.get("/sources/{student_id}")
def get_sources(student_id: str):
    if student_id not in store:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"sources": store[student_id]}

@app.post("/sources/{student_id}")
def add_source(student_id: str, payload: dict):
    if student_id != STUDENT_ID:
        raise HTTPException(status_code=404, detail="Student not found")
    url = payload.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    store[student_id].append(url)
    return {"sources": store[student_id]}

@app.post("/fetch/{student_id}")
def fetch_news(student_id: str):
    if student_id != STUDENT_ID:
        raise HTTPException(status_code=404, detail="Student not found")

    if student_id not in news_store:
        news_store[student_id] = []

    news_store[student_id].clear()
    fetched = 0

    sources = store.get(student_id, config.SOURCES)
    for url in sources:
        feed = feedparser.parse(url)
        for entry in getattr(feed, "entries", []):
            news_store[student_id].append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "published": entry.get("published", "")
            })
            fetched += 1

    return {"fetched": fetched}

@app.get("/news/{student_id}")
def get_news(student_id: str):
    if student_id not in news_store:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"articles": news_store[student_id]}

@app.post("/analyze/{student_id}")
def analyze_tone(student_id: str):
    if student_id != STUDENT_ID:
        raise HTTPException(status_code=404, detail="Student not found")

    articles = news_store.get(student_id, [])
    result = []

    for art in articles:
        text = art.get("title", "")
        scores = analyzer.polarity_scores(text)
        comp = scores["compound"]
        if comp >= 0.05:
            label = "positive"
        elif comp <= -0.05:
            label = "negative"
        else:
            label = "neutral"
        result.append({**art, "sentiment": label, "scores": scores})

    return {"analyzed": len(result), "articles": result}

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    print("Login endpoint called")
    try:
        username = form_data.username
        password = form_data.password
        print(f"Received username={username} password={password}")

        user = fake_users_db.get(username)
        if not user or user["password"] != password:
            print("Invalid credentials")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        print("Login successful")
        return {"access_token": "fake-token-for-demo", "token_type": "bearer"}
    except Exception as e:
        print(f"Error in /token: {e}")
        raise

@app.get("/fetch-and-show/{student_id}")
def fetch_and_show(student_id: str):
    if student_id != STUDENT_ID:
        raise HTTPException(status_code=404, detail="Student not found")

    if student_id not in news_store:
        news_store[student_id] = []

    news_store[student_id].clear()
    fetched = 0

    for url in config.SOURCES:
        feed = feedparser.parse(url)
        for entry in getattr(feed, "entries", []):
            news_store[student_id].append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "published": entry.get("published", "")
            })
            fetched += 1

    return {
        "fetched": fetched,
        "articles": news_store[student_id]
    }

# Кастомна OpenAPI-документація

def clear_test_data():
    store[STUDENT_ID] = []
    news_store[STUDENT_ID] = []
    sources_store[STUDENT_ID] = []

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="News Aggregator API",
        version="1.0",
        description="API для новин із авторизацією",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "token"
                }
            }
        }
    }
    openapi_schema["security"] = [{"OAuth2PasswordBearer": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

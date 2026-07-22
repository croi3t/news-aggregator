from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from dotenv import load_dotenv
import database
import notifier
import worker
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

# 環境変数の読み込み
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = BackgroundScheduler()
    # 起動時にすぐ実行し、以降は1時間ごとに実行する
    scheduler.add_job(worker.process_feeds, trigger='interval', hours=1, next_run_time=datetime.now())
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(title="News Aggregator", lifespan=lifespan)

# 静的ファイルとテンプレートの設定
# os.makedirs("static", exist_ok=True)
# os.makedirs("templates", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class FeedCreate(BaseModel):
    title: str
    url: str
    category: str

@app.post("/add_feed")
async def api_add_feed(feed: FeedCreate):
    success = database.add_feed(feed.title, feed.url, feed.category)
    if success:
        return JSONResponse(content={"status": "success", "message": "Feed added successfully."})
    else:
        return JSONResponse(status_code=400, content={"status": "error", "message": "Failed to add feed. It might already exist."})

class ArchiveRequest(BaseModel):
    title: str
    url: str
    summary: str

@app.post("/archive")
async def api_archive(req: ArchiveRequest):
    message = f"【保存した記事】\n{req.title}\n\n{req.url}\n\n{req.summary}"
    notifier.send_line_message(message)
    return JSONResponse(content={"status": "success", "message": "Archived to LINE"})

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # DBからフィードと記事を取得
    feeds = database.get_all_feeds()
    articles = database.get_recent_articles(limit=50)
    # 記事に付与されたAIタグ一覧を取得
    categories = list(set([a['category'] for a in articles]))
    
    return templates.TemplateResponse(request=request, name="index.html", context={"feeds": feeds, "articles": articles, "categories": categories})

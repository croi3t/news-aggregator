import sqlite3
from datetime import datetime

DB_FILE = "news_aggregator.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # feeds table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feeds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL
        )
    ''')
    
    # articles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            feed_id INTEGER,
            title TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
            summary TEXT,
            category TEXT NOT NULL,
            published_at TEXT,
            is_read INTEGER DEFAULT 0,
            created_at TEXT,
            FOREIGN KEY (feed_id) REFERENCES feeds (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# DB操作のヘルパー関数群
def seed_default_feeds():
    conn = get_db_connection()
    count = conn.execute('SELECT COUNT(*) FROM feeds').fetchone()[0]
    if count == 0:
        default_feeds = [
            ("Yahoo! 国内", "https://news.yahoo.co.jp/rss/topics/domestic.xml", "国内"),
            ("Yahoo! 政治・国際", "https://news.yahoo.co.jp/rss/topics/world.xml", "国際"),
            ("Yahoo! 地域", "https://news.yahoo.co.jp/rss/topics/local.xml", "地域"),
            ("Yahoo! 経済", "https://news.yahoo.co.jp/rss/topics/business.xml", "経済"),
            ("Yahoo! IT・テクノロジー", "https://news.yahoo.co.jp/rss/topics/it.xml", "IT"),
            ("Yahoo! 科学", "https://news.yahoo.co.jp/rss/topics/science.xml", "サイエンス"),
            ("Yahoo! ライフ (料理・健康)", "https://news.yahoo.co.jp/rss/topics/life.xml", "ライフスタイル"),
            ("Yahoo! エンタメ (アイドル等)", "https://news.yahoo.co.jp/rss/topics/entertainment.xml", "エンタメ"),
            ("Google 検索 (料理・レシピ)", "https://news.google.com/rss/search?q=%E6%96%99%E7%90%86+OR+%E3%83%AC%E3%82%B7%E3%83%94&hl=ja&gl=JP&ceid=JP:ja", "料理"),
            ("Google 検索 (旅行・観光)", "https://news.google.com/rss/search?q=%E6%97%85%E8%A1%8C+OR+%E8%A6%B3%E5%85%89&hl=ja&gl=JP&ceid=JP:ja", "旅行"),
            ("Google 検索 (音楽)", "https://news.google.com/rss/search?q=%E9%9F%B3%E6%A5%BD&hl=ja&gl=JP&ceid=JP:ja", "音楽"),
            ("Google 検索 (ゲーム セール情報)", "https://news.google.com/rss/search?q=%E3%82%B2%E3%83%BC%E3%83%A0+%E3%82%BB%E3%83%BC%E3%83%AB&hl=ja&gl=JP&ceid=JP:ja", "ゲームセール"),
            ("Google 検索 (新薬承認)", "https://news.google.com/rss/search?q=%E6%96%B0%E8%96%AC+%E6%89%BF%E8%AA%8D&hl=ja&gl=JP&ceid=JP:ja", "新薬"),
            ("Discover (Nature)", "https://www.nature.com/nature.rss", "Discover"),
            ("Discover (Science)", "https://www.science.org/rss/news_current.xml", "Discover"),
            ("Discover (NatGeo)", "https://natgeo.nikkeibp.co.jp/nng/index.rdf", "Discover"),
            ("Discover (WIRED)", "https://wired.jp/feed/", "Discover"),
            ("Google 検索 (グラビア)", "https://news.google.com/rss/search?q=グラビア&hl=ja&gl=JP&ceid=JP:ja", "グラビア"),
            ("4Gamer (ゲーム)", "https://www.4gamer.net/rss/index.xml", "ゲーム"),
            ("アニメ!アニメ!", "https://animeanime.jp/feed/", "アニメ"),
            ("arXiv 最新論文 (AI)", "https://rss.arxiv.org/rss/cs.AI", "論文"),
            ("PubMed (Clinical - Anticoagulants 1)", "https://pubmed.ncbi.nlm.nih.gov/rss/search/1hMQ8bQB8dXQ7M5Jeeu5vs1S4e10RKo8wNc-4xNcOmWhn9fEki/?limit=15&utm_campaign=pubmed-2&fc=20260727052501", "論文"),
            ("PubMed (Clinical - Stroke 1)", "https://pubmed.ncbi.nlm.nih.gov/rss/search/1linSS9uJPl6kgexOfx8t7ja7gzedAmqJyvQHTxJ80mOQQhsMM/?limit=15&utm_campaign=pubmed-2&fc=20260727052527", "論文"),
            ("PubMed (Clinical - Anticoagulants 2)", "https://pubmed.ncbi.nlm.nih.gov/rss/search/1hCS5QvDf5qZRm4wiVrrHTVNQwxiTRtq5W7SfDeXPYdkAKgkYE/?limit=15&utm_campaign=pubmed-2&fc=20260727053752", "論文"),
            ("PubMed (Clinical - Stroke 2)", "https://pubmed.ncbi.nlm.nih.gov/rss/search/1TcjM2U847Oztqfm_9EIfbBE88pDZ7bxcBVNCU-Y152oSGlYTk/?limit=15&utm_campaign=pubmed-2&fc=20260727053810", "論文")
        ]
        cursor = conn.cursor()
        for title, url, category in default_feeds:
            cursor.execute('INSERT OR IGNORE INTO feeds (title, url, category) VALUES (?, ?, ?)', (title, url, category))
        conn.commit()
    conn.close()

# 初期化の実行
init_db()
seed_default_feeds()

def get_all_feeds():
    conn = get_db_connection()
    feeds = conn.execute('SELECT * FROM feeds').fetchall()
    conn.close()
    return [dict(row) for row in feeds]

def add_feed(title, url, category):
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO feeds (title, url, category) VALUES (?, ?, ?)', (title, url, category))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_recent_articles(limit=200):
    conn = get_db_connection()
    articles = conn.execute('SELECT * FROM articles ORDER BY published_at DESC LIMIT ?', (limit,)).fetchall()
    conn.close()
    return [dict(row) for row in articles]

def add_article(feed_id, title, url, summary, category, published_at):
    conn = get_db_connection()
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute('''
            INSERT OR REPLACE INTO articles (feed_id, title, url, summary, category, published_at, created_at) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (feed_id, title, url, summary, category, published_at, now))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def article_exists(url, title):
    conn = get_db_connection()
    row = conn.execute('SELECT summary, category FROM articles WHERE url = ? OR title = ?', (url, title)).fetchone()
    conn.close()
    
    if row:
        # エラーだった記事の場合は未処理とみなして再処理（False）させる
        if row['summary'] == '要約の生成に失敗しました。' or row['category'] == 'Error':
            return False
        return True
    return False

def get_recent_titles(limit=200):
    conn = get_db_connection()
    rows = conn.execute('SELECT title FROM articles ORDER BY published_at DESC LIMIT ?', (limit,)).fetchall()
    conn.close()
    return [row['title'] for row in rows]

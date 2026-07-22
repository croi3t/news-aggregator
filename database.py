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
            ("Yahoo! 政治", "https://news.yahoo.co.jp/rss/categories/domestic.xml", "政治"),
            ("Yahoo! 経済", "https://news.yahoo.co.jp/rss/topics/business.xml", "経済"),
            ("Yahoo! IT・テクノロジー", "https://news.yahoo.co.jp/rss/topics/it.xml", "IT"),
            ("Yahoo! 科学", "https://news.yahoo.co.jp/rss/topics/science.xml", "サイエンス"),
            ("Yahoo! ライフ (料理・健康)", "https://news.yahoo.co.jp/rss/topics/life.xml", "ライフスタイル"),
            ("Yahoo! エンタメ (アイドル等)", "https://news.yahoo.co.jp/rss/topics/entertainment.xml", "エンタメ"),
            ("4Gamer (ゲーム)", "https://www.4gamer.net/rss/index.xml", "ゲーム"),
            ("アニメ!アニメ!", "https://animeanime.jp/feed/", "アニメ"),
            ("arXiv 最新論文 (AI)", "https://rss.arxiv.org/rss/cs.AI", "論文")
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

def get_recent_articles(limit=50):
    conn = get_db_connection()
    articles = conn.execute('SELECT * FROM articles ORDER BY published_at DESC LIMIT ?', (limit,)).fetchall()
    conn.close()
    return [dict(row) for row in articles]

def add_article(feed_id, title, url, summary, category, published_at):
    conn = get_db_connection()
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute('''
            INSERT INTO articles (feed_id, title, url, summary, category, published_at, created_at) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (feed_id, title, url, summary, category, published_at, now))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

import feedparser
from datetime import datetime
from bs4 import BeautifulSoup

def clean_html(html_content):
    """HTMLタグを除去してプレーンテキストを抽出する"""
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text(separator=' ', strip=True)

def fetch_feed_articles(feed_url: str, limit: int = 5):
    """
    指定されたRSSフィードから最新の記事を取得する
    """
    parsed_feed = feedparser.parse(feed_url)
    articles = []
    
    for entry in parsed_feed.entries[:limit]:
        title = entry.get('title', '')
        link = entry.get('link', '')
        
        # summaryやdescriptionなど、利用可能な本文を取得
        content = entry.get('content', [{'value': ''}])[0].get('value', '')
        if not content:
            content = entry.get('summary', '')
            
        content_text = clean_html(content)
        
        # 取得できた文字数が極端に少ない場合は要約しないなどの判断が可能
        published = entry.get('published', '')
        
        articles.append({
            'title': title,
            'link': link,
            'content': content_text,
            'published': published
        })
        
    return articles

if __name__ == "__main__":
    # テスト用 (ITmedia 総合ニュースのRSS)
    test_url = "https://rss.itmedia.co.jp/rss/2.0/itmedia_all.xml"
    res = fetch_feed_articles(test_url, 2)
    for r in res:
        print(f"Title: {r['title']}")
        print(f"Published: {r['published']}")
        print(f"Content length: {len(r['content'])}")
        print("---")

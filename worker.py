import database
import fetcher
import summarizer
import time

def process_feeds():
    """登録されているすべてのフィードから記事を取得・要約してDBに保存するバッチ処理"""
    print("=== Starting Feed Processing ===")
    
    # DBからフィード一覧を取得
    feeds = database.get_all_feeds()
    
    if not feeds:
        print("No feeds found. Please add feeds to the database.")
        return

    for feed in feeds:
        feed_id = feed['id']
        feed_url = feed['url']
        feed_category = feed['category']
        feed_title = feed['title']
        
        print(f"\nProcessing feed: {feed_title} ({feed_url})")
        
        # 記事の取得
        # 各フィードにつき最新5件までに制限（API制限回避のため）
        articles = fetcher.fetch_feed_articles(feed_url, limit=5)
        
        for article in articles:
            title = article['title']
            url = article['link']
            published_at = article['published']
            
            # 記事の内容を取得（要約に使うため）
            content = ""
            if article.get('content'):
                article_content = article.get('content')
                if isinstance(article_content, list) and len(article_content) > 0:
                    content = article_content[0].get('value', '')
                elif isinstance(article_content, str):
                    content = article_content
            if not content:
                content = article.get('summary', '')

            print(f"  - Summarizing: {title}")
            
            # Gemini APIの無料枠制限（15回/分）を回避するため4.2秒待機
            time.sleep(4.2)
            ai_result = summarizer.summarize_text(title, content)
            
            summary = ai_result.get("summary", "要約の生成に失敗しました。")
            ai_category = ai_result.get("tag", feed_category) # 失敗時は元のカテゴリを使用
            
            # DBに保存
            success = database.add_article(
                feed_id=feed_id,
                title=title,
                url=url,
                summary=summary,
                category=ai_category,
                published_at=published_at
            )
            
            if success:
                print(f"    -> Saved successfully.")
            else:
                print(f"    -> Already exists or error.")
                
            # APIのレートリミット対策で少し待機
            time.sleep(2)

    print("=== Feed Processing Finished ===")

if __name__ == "__main__":
    # テストとして、DBに1件フィードがなければ追加して実行する
    feeds = database.get_all_feeds()
    if not feeds:
        print("Adding sample feed...")
        database.add_feed("ITmedia 総合", "https://rss.itmedia.co.jp/rss/2.0/itmedia_all.xml", "IT")
        
    process_feeds()

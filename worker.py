import database
import fetcher
import difflib

def process_feeds():
    """登録されているすべてのフィードから記事を取得・要約してDBに保存するバッチ処理"""
    print("=== Starting Feed Processing ===")
    
    # DBからフィード一覧を取得し、PubMedを優先（先頭）にするようソート
    feeds = database.get_all_feeds()
    feeds.sort(key=lambda x: "pubmed" not in x['url'].lower())
    
    if not feeds:
        print("No feeds found. Please add feeds to the database.")
        return

    # 類似記事チェック用に最近のタイトル一覧を取得
    recent_titles = database.get_recent_titles(200)

    for feed in feeds:
        feed_id = feed['id']
        feed_url = feed['url']
        feed_category = feed['category']
        feed_title = feed['title']
        
        print(f"\nProcessing feed: {feed_title} ({feed_url})")
        
        # 記事の取得
        # 取得件数を大幅に引き上げ（最大50件）
        articles = fetcher.fetch_feed_articles(feed_url, limit=50)
        
        for article in articles:
            title = article['title']
            url = article['link']
            published_at = article['published']
            
            # すでにデータベースに同じURLかタイトルの記事があれば、無駄なAI処理をスキップする
            if database.article_exists(url, title):
                continue
                
            # 類似タイトルの除外 (80%以上一致する場合はスキップ)
            is_similar = False
            for rt in recent_titles:
                if difflib.SequenceMatcher(None, title, rt).ratio() > 0.8:
                    is_similar = True
                    break
            
            if is_similar:
                print(f"  - Skipping similar article: {title.encode('cp932', 'replace').decode('cp932')}")
                continue
                
            # この実行内で処理された記事も類似チェック対象に追加
            recent_titles.append(title)
            
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

            # Windows環境等で特殊な文字（絵文字など）を表示しようとして強制終了するのを防ぐ
            safe_title = title.encode('cp932', 'replace').decode('cp932')
            print(f"  - Saving: {safe_title}")
            
            # AIは使用せず、元のテキストをそのまま保存して超高速化する
            ai_category = "PubMed" if "pubmed" in feed_url.lower() else feed_category
            
            # PubMedの場合は文字制限を解除し全文保存
            if "pubmed" in feed_url.lower():
                raw_summary = content if content else "（本文がありません）"
            else:
                # PubMed以外は冒頭300文字を抽出。改行もそのまま保持させる。
                raw_summary = (content[:300] + "...") if content else "（本文がありません）"
                
            summary = raw_summary
            
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

    print("=== Feed Processing Finished ===")

if __name__ == "__main__":
    # テストとして、DBに1件フィードがなければ追加して実行する
    feeds = database.get_all_feeds()
    if not feeds:
        print("Adding sample feed...")
        database.add_feed("ITmedia 総合", "https://rss.itmedia.co.jp/rss/2.0/itmedia_all.xml", "IT")
        
    process_feeds()

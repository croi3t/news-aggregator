import os
import requests
from dotenv import load_dotenv

load_dotenv()

LINE_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

def send_line_message(message: str):
    """LINE Messaging API (Push Message) を使用して通知を送信する"""
    if not LINE_TOKEN:
        print("LINE_CHANNEL_ACCESS_TOKEN is not set. Skipping LINE notification.")
        print(f"Message preview:\n{message}")
        return False
        
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_TOKEN}"
    }
    data = {
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Failed to send LINE message: {e}")
        return False

def notify_new_articles(count: int):
    """新しい記事が追加されたときに通知を送る"""
    message = f"【AI News Aggregator】\n新しく {count} 件の記事が取得・要約されました！\n\nアプリを開いて確認してください。"
    send_line_message(message)

if __name__ == "__main__":
    notify_new_articles(3)

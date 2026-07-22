import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

# クライアントの初期化
client = genai.Client(api_key=API_KEY)

import json

def summarize_text(title: str, content: str) -> dict:
    """記事のタイトルと内容を元に要約とAIタグを生成する"""
    if not API_KEY:
        return "Error: Gemini API key is not set."
        
    prompt = f"""
以下の記事を読み、スマホの画面でサクッと読めるように日本語で要約してください。
なるべく箇条書きを用い、重要なポイントを3つ程度に絞ってください。

また、この記事に最も適した大まかなジャンル（タグ）を1単語で判定してください。
（例：IT, 経済, 政治, エンタメ, スポーツ, ライフスタイル, サイエンス, その他）

以下のJSONフォーマットのみを出力してください。バッククォートなどのマークダウン修飾は不要です。
{{
    "tag": "大まかなジャンル名",
    "summary": "要約のテキスト..."
}}

タイトル: {title}
内容: {content}
"""

    try:
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt,
        )
        
        # 稀に ```json と ``` が付くことがあるので除去
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
            
        result = json.loads(text.strip())
        return result
    except Exception as e:
        print(f"Summarization error: {e}")
        return {"summary": "要約の生成に失敗しました。", "tag": "Error"}

if __name__ == "__main__":
    # テスト用
    print(summarize_text("テスト記事", "これはテスト用の記事本文です。AIが内容を分析して要約を作成します。"))

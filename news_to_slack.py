import os
import requests
from openai import OpenAI
from datetime import datetime

# 環境変数から取得
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL')
NEWS_API_KEY = os.environ.get('NEWS_API_KEY')  # オプション

# 曜日ごとのニュースジャンル設定
WEEKLY_TOPICS = {
    0: {  # 月曜日
        "name": "音楽ストリーミング",
        "keywords": "音楽ストリーミングサービス(Apple Music, Spotify, Amazon Music)"
    },
    1: {  # 火曜日
        "name": "音楽×AI",
        "keywords": "音楽業界のAI"
    },
    2: {  # 水曜日
        "name": "音楽ビジネス",
        "keywords": "国内外の音楽ビジネス全般"
    },
    3: {  # 木曜日
        "name": "音楽トレンド",
        "keywords": "国内外の音楽トレンド"
    },
    4: {  # 金曜日
        "name": "生成AI",
        "keywords": "生成AI"
    }
}

def get_today_topic():
    """今日の曜日に応じたトピックを取得"""
    weekday = datetime.now().weekday()
    return WEEKLY_TOPICS[weekday]

def search_news_with_chatgpt(topic):
    """ChatGPTにニュース検索を依頼"""
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    today = datetime.now().strftime('%Y年%m月%d日')
    keywords_str = "、".join(topic["keywords"])
    
    prompt = f"""今日は{today}です。
直近7日間にあった、「{topic['name']}」に関する最新のニュースを検索して、以下の形式でまとめてください：

以下の情報を含めてください：
1. 最新の主要ニュース3-5件のタイトルと要点
2. 全体的なトレンドや傾向
3. 注目すべきポイント

日本語で、親しみやすく読みやすい形式でお願いします。
実際のニュースを検索して、具体的な情報を提供してください。
対話はせずにニュースの情報だけ伝えてください。(相手に返事を促すようなコメントはしない)
"""

    response = client.responses.create(
        model="gpt-4o",
        input=prompt,
        tools=[{"type": "web_search"}]  # 検索ツールを使うよう指定
    )
    
    # response = client.chat.completions.create(
    #     model="gpt-4o",  # 検索機能を使うためgpt-4oを推奨
    #     messages=[
    #         {"role": "system", "content": "あなたは最新ニュースを検索して分かりやすくまとめるアシスタントです。"},
    #         {"role": "user", "content": prompt}
    #     ],
    #     max_tokens=1500,
    #     temperature=0.7
    # )
    
    # return response.choices[0].message.content
    return response.output_text

def post_to_slack(message, topic):
    """Slackに投稿"""
    today = datetime.now().strftime('%Y年%m月%d日 (%A)')
    weekday_jp = ["月", "火", "水", "木", "金", "土", "日"][datetime.now().weekday()]
    
    payload = {
        "text": f"📰 *{today} - {topic['name']}ニュース*\n\n{message}"
    }
    
    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    
    if response.status_code == 200:
        print("✅ Slackへの投稿に成功しました")
    else:
        print(f"❌ エラー: {response.status_code}")
        print(response.text)

def main():
    # 今日のトピックを取得
    topic = get_today_topic()
    print(f"📅 今日は{topic['name']}の日です")
    
    try:
        # ChatGPTにニュース検索を依頼（推奨方法）
        print("ChatGPTでニュースを検索中...")
        summary = search_news_with_chatgpt(topic)
        
        print("Slackに投稿中...")
        post_to_slack(summary, topic)
        
    except Exception as e:
        print(f"⚠️ ChatGPT検索でエラー: {e}")
        print(f"slackへの投稿はスキップします")
    
    print("✅ 完了！")

if __name__ == "__main__":
    main()

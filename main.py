import os
import sys
import json
import requests
from google.cloud import storage
import discord_webhook

BUCKET_NAME = os.environ.get("BUCKET_NAME")
if not BUCKET_NAME:
    print("BUCKET_NAMEが設定されていません。")
    sys.exit(1)

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
if not DISCORD_WEBHOOK_URL:
    print("DISCORD_WEBHOOK_URLが設定されていません。")
    sys.exit(1)

game_id = "o1y9zk26"

hardwares = [
    "gnxrw1jn=21g48jm1", # PC
    "gnxrw1jn=jqz5p6mq"  # Console
]

sub_categories_file = "subcategories.json"
wr_list_file = "wr_list.json"

runs_url = f"https://www.speedrun.com/api/v1/runs?game={game_id}&status=verified&orderby=verify-date&direction=desc"

def load_wr_list():
    """WRリストをJSONファイルから読み込む"""
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(wr_list_file)
    if blob.exists():
        content = blob.download_as_string()
        return json.loads(content)
    return []

def save_wr_list(wr_list):
    """WRリストをJSONファイルに保存する"""
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    try:
        blob = bucket.blob(wr_list_file)
        blob.upload_from_string(json.dumps(wr_list, indent=4))
    except Exception as e:
        print(f"WRリストの保存に失敗しました: {e}")

def get_recent_runs():
    """最近の記録をSpeedrun.com APIから取得する"""
    response = requests.get(runs_url)
    response.raise_for_status()
    if response.status_code == 200:
        if response.json().get("data"):
            return response.json().get("data")
    return []

def compare_runs(recent_runs, wr_list):
    """最近の記録とWRリストを比較して新しい記録を特定する"""
    new_record_video_list = []
    for run in recent_runs:
        recent_runs_hardware = run.get("values", {}).get("gnxrw1jn")
        recent_runs_sub_category = run.get("values", {}).get("ylqkog7l")
        recent_runs_time = run.get("times", {}).get("primary_t")

        for wr in wr_list:
            if (wr["hardware"] == f'gnxrw1jn={recent_runs_hardware}' and 
                wr["value"] == recent_runs_sub_category):
                if wr["wr_time"] > recent_runs_time:
                    wr["wr_time"] = recent_runs_time
                    video_links = run.get("videos", {}).get("links", [])
                    video_url = video_links[0].get("uri") if video_links else "動画リンクなし"
                    new_record_video_list.append(video_url)
    return wr_list, new_record_video_list

def send_discord_message(content):
    """Discord Webhookにメッセージを送信する"""
    if not DISCORD_WEBHOOK_URL:
        print("DISCORD_WEBHOOK_URLが設定されていません。通知をスキップします。")
        return
        
    webhook = discord_webhook.DiscordWebhook(url=DISCORD_WEBHOOK_URL, content=content)
    response = webhook.execute()
    
    if not response.ok:
        print(f"Discord通知に失敗しました。ステータスコード: {response.status_code}")

def load_sub_categories():
    try:
        with open(sub_categories_file, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"サブカテゴリの読み込みに失敗しました: {e}")
        sys.exit(1)
        
def get_wr_time(url):
    response = requests.get(url)
    response.raise_for_status()
    data = response.json().get("data", {})
    if data:
        if data.get("runs"):
            return data.get("runs")[0].get("run", {}).get("times", {}).get("primary_t", 99999)
    return 99999

def get_wr(sub_categories):
    wr_list = []
    for hardware in hardwares:
        for sub_category in sub_categories:
            category_id = sub_category["id"]
            category_name = sub_category["category"]
            values = sub_category["values"]
            for value in values:
                url = f"https://www.speedrun.com/api/v1/leaderboards/{game_id}/category/{category_name}?var-{hardware}&var-{category_id}={value}&top=1"
                wr_time = get_wr_time(url)
                wr_list.append({
                    "hardware": hardware,
                    "category_id": category_id,
                    "value": value,
                    "wr_time": wr_time
                })
    return wr_list

def main():
    # 現在のWRリストを読み込む
    wr_list = load_wr_list()

    if wr_list == []:
        sub_categories = load_sub_categories()
        try:
            with open(wr_list_file, "w") as f:
                wr_list = get_wr(sub_categories)
                if wr_list == []:
                    print("WRリストの取得に失敗しました。")
                    sys.exit(1)
                save_wr_list(wr_list)
        except Exception as e:
            print(f"WRリストの保存に失敗しました: {e}")
            sys.exit(1)

    # 最近の記録を取得する
    recent_runs = get_recent_runs()
    if recent_runs == []:
        print("最近の記録の取得に失敗しました。")
        sys.exit(1)

    # 最近の記録とWRリストを比較して新しい記録を特定する
    updated_wr_list, new_records = compare_runs(recent_runs, wr_list)

    if new_records:
        print(f"{len(new_records)} 件の新しい記録が見つかりました。")
        # Discordに通知する
        for record in new_records:
            message = f"世界記録が更新されました！\n動画URL: {record}"
            print(message)  # デバッグ用にコンソールにも出力
            send_discord_message(message)

        # 更新されたWRリストを保存する
        save_wr_list(updated_wr_list)
    else:
        print("新しい記録はありませんでした。")
    sys.exit(0)

if __name__ == "__main__":
    main()

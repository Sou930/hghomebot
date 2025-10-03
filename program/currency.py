import json
from pathlib import Path
from datetime import datetime, timedelta

# 保存先ファイル
DATA_FILE = Path("Data/currency.json")
BONUS_HOURS = 20  # ログインボーナス間隔（20時間）

def load_data():
    """ユーザーデータを読み込む"""
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    """ユーザーデータを保存する"""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_currency(user_id, amount):
    """ユーザーの所持金を増減する"""
    data = load_data()
    user = data.get(str(user_id), {"balance": 0, "last_daily": None})
    user["balance"] += amount
    data[str(user_id)] = user
    save_data(data)
    return user["balance"]

def can_receive_daily(user_id):
    """ログインボーナスを受け取れるか確認"""
    data = load_data()
    user = data.get(str(user_id))
    if not user or not user.get("last_daily"):
        return True
    last_claim = datetime.fromisoformat(user["last_daily"])
    return (datetime.utcnow() - last_claim) >= timedelta(hours=BONUS_HOURS)

def claim_daily(user_id, amount):
    """ログインボーナスを受け取る"""
    data = load_data()
    user = data.get(str(user_id), {"balance": 0, "last_daily": None})

    if can_receive_daily(user_id):
        user["balance"] += amount
        user["last_daily"] = datetime.utcnow().isoformat()
        data[str(user_id)] = user
        save_data(data)
        return True, user["balance"]
    else:
        return False, user["balance"]

def get_balance(user_id):
    """現在の所持金を取得"""
    data = load_data()
    user = data.get(str(user_id), {"balance": 0})
    return user["balance"]

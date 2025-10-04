# DATA/firebase_db.py
from DATA.firebase_init import init_firebase  # DATA内からの相対インポート

db = init_firebase()

def get_user_balance(discord_id: int) -> int:
    doc_ref = db.collection("users").document(str(discord_id))
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict().get("balance", 0)
    else:
        doc_ref.set({"balance": 0})
        return 0

def set_user_balance(discord_id: int, amount: int):
    doc_ref = db.collection("users").document(str(discord_id))
    doc_ref.update({"balance": amount})
    
# --- チャンネルカウント関連 ---
def get_channel_state(channel_id: int) -> dict:
    doc_ref = db.collection("count_channels").document(str(channel_id))
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    return {
        "last_number": 0,
        "last_user": None,
        "success": 0,
        "fails": 0,
        "resets": 0
    }

def set_channel_state(channel_id: int, state: dict):
    doc_ref = db.collection("count_channels").document(str(channel_id))
    data = state.copy()
    data.pop("lock", None)  # Lockは保存しない
    doc_ref.set(data)

def delete_channel_state(channel_id: int):
    doc_ref = db.collection("count_channels").document(str(channel_id))
    doc_ref.delete()

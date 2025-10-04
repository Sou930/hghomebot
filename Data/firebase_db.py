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

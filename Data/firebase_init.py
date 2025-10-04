import firebase_admin
from firebase_admin import credentials, firestore
import os

db = None  # Firestoreクライアント

def init_firebase():
    """
    Firebaseを初期化して、dbを使えるようにする
    Renderの環境変数でサービスアカウントJSONを渡す
    """
    global db

    # Renderに JSON を環境変数で保存している場合
    cred_json = os.environ.get("FIREBASE_CRED_JSON")
    if not cred_json:
        raise RuntimeError("FIREBASE_CRED_JSON が環境変数に設定されていません")

    import json
    cred_dict = json.loads(cred_json)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✅ Firebase initialized")

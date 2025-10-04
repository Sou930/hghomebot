import firebase_admin
from firebase_admin import credentials, firestore
import os, json

def init_firebase():
    # Render環境変数からJSON文字列を取得
    firebase_key_str = os.environ.get("FIREBASE_KEY")
    if not firebase_key_str:
        raise ValueError("FIREBASE_KEY 環境変数が設定されていません")

    # JSON文字列を辞書に変換
    firebase_key_dict = json.loads(firebase_key_str)

    # Firebase初期化（複数回初期化防止）
    if not firebase_admin._apps:
        cred = credentials.Certificate(firebase_key_dict)
        firebase_admin.initialize_app(cred)

    # Firestoreクライアントを返す
    return firestore.client()

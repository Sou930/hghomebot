# HGHomeBot

RenderでホストされているDiscord多機能Botです。  
モジュール式構成により、各機能を独立して開発・更新できます。

---

## 📦 現在のバージョン
**v1.1.1**

### 🔄 バージョンルール
`v1(大幅変更).0(新要素).0(バグ修正)`  
例: `v1.10.3` なども可能です。

---

## 🧩 ディレクトリ構成
hghomebot/
├── Data/
│ ├── currency.json # 通貨データ
│ └── （その他データファイル）
├── program/
│ ├── currency.py # 通貨システム
│ ├── casino.py # カジノ機能（v1.1.1〜）
│ └── （その他モジュール）
├── main.py # Botのエントリーポイント
├── keep_alive.py # Render用サーバー維持スクリプト
├── requirements.txt # 使用ライブラリ一覧
└── Dockerfile # Renderビルド設定


---

## ⚙️ 機能一覧

### 💰 通貨システム（v1.1.0〜）
- `/daily` … 20時間おきにログインボーナスを受け取る  
- `/balance` … 所持金を確認する  
- `/top type:balance` … 所持金ランキングを表示（データがない場合は「データがありません」と表示）

---

### 🎰 カジノ機能（v1.1.1〜）
- `/casino type: bet:`  
  - **type 候補:**  
    - `slot` … スロット  
    - `cointoss` … コイントス  

💡 `/casino` の実行結果により、勝敗に応じて通貨が増減します。

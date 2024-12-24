import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
from collections import Counter
import json
import os

# アイコン画像の表示（画像をプロジェクト内のassetsフォルダに配置）
st.image("assets/your_icon.png", width=100)  # 画像のパスを指定

# Firebaseの初期化（重複初期化を防ぐための条件追加）
if not firebase_admin._apps:
    # Streamlit SecretsからFirebase認証情報を取得
    firebase_credentials = {
        "type": st.secrets["firebase"]["type"],
        "project_id": st.secrets["firebase"]["project_id"],
        "private_key_id": st.secrets["firebase"]["private_key_id"],
        "private_key": st.secrets["firebase"]["private_key"],
        "client_email": st.secrets["firebase"]["client_email"],
        "client_id": st.secrets["firebase"]["client_id"],
        "auth_uri": st.secrets["firebase"]["auth_uri"],
        "token_uri": st.secrets["firebase"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"]
    }
    
    # credentials.Certificateにはファイルパスではなく辞書を渡す
    cred = credentials.Certificate(firebase_credentials)
    firebase_admin.initialize_app(cred)

# Firestoreクライアント
db = firestore.client()

# Firestoreからデータを読み込む関数
def load_data():
    docs = db.collection("restaurants").stream()
    data = []
    for doc in docs:
        data.append(doc.to_dict())
    return pd.DataFrame(data)

# Firestoreにデータを追加する関数
def add_restaurant(name, dish, location):
    doc_ref = db.collection("restaurants").document()
    doc_ref.set({
        "name": name,
        "dish": dish,
        "location": location
    })

# アプリのタイトル
st.title("📌 みんなのおすすめレストラン")

# Firestoreからデータを読み込み
data = load_data()

# おすすめ一覧を表示
st.subheader("📋 現在のおすすめレストラン一覧")
if data.empty:
    st.write("まだ登録されたレストランがありません。")
else:
    st.dataframe(data)

# 新しいレストランを追加
st.subheader("✍️ あなたのおすすめを追加")
with st.form("add_restaurant_form"):
    name = st.text_input("店名")
    dish = st.text_input("おすすめ料理")
    location = st.text_input("場所（例: 名古屋市）")
    submitted = st.form_submit_button("追加する")
    
    if submitted:
        if name and dish and location:
            add_restaurant(name, dish, location)
            st.success(f"店名 '{name}' を追加しました！")
        else:
            st.error("すべてのフィールドを入力してください。")

# 集計とランキング表示
if not data.empty:
    st.subheader("🏆 人気ランキング")

    # 店名のランキング
    restaurant_counts = Counter(data["name"])
    restaurant_ranking = pd.DataFrame(restaurant_counts.items(), columns=["店名", "出現回数"]).sort_values(by="出現回数", ascending=False).head(5)
    st.write("🔝 店名ランキング（トップ5）")
    st.dataframe(restaurant_ranking)

    # 料理のランキング
    dish_counts = Counter(data["dish"])
    dish_ranking = pd.DataFrame(dish_counts.items(), columns=["料理", "出現回数"]).sort_values(by="出現回数", ascending=False).head(5)
    st.write("🔝 料理ランキング（トップ5）")
    st.dataframe(dish_ranking)

# インスタグラムのリンク
st.subheader("📲 Instagramでシェアしてね！")
st.markdown("""
    <a href="https://www.instagram.com/momo_nagoyafood" target="_blank">
        <button style="background-color: #e4405f; color: white; padding: 10px 20px; border-radius: 8px; font-size: 18px; border: none;">
            Instagramでシェア
        </button>
    </a>
""", unsafe_allow_html=True)



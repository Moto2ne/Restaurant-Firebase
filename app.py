import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
from collections import Counter

# Firebaseの初期化（重複初期化を防ぐための条件追加）
if not firebase_admin._apps:
    cred = credentials.Certificate("C:/momo/restaurant-app/firebase_key.json")  # サービスアカウントキーのパス
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
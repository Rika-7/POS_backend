from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

# CORSミドルウェアを追加
# これにより、フロントエンド（Next.js）からのリクエストを許可します
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tech0-gen-7-step4-studentwebapp-pos-7-grfff0e3a4cmcvfg.eastus-01.azurewebsites.net"],  # フロントエンドのURLを指定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"おはよう！": "元気？"}

# 商品の一覧を取得するエンドポイント
@app.get("/items")
async def get_items(code: str = Query(None)):
    # ここでデータベースから商品一覧を取得する処理を実装します
    # 仮のデータを返します
    if code == "123":
        return {"id": 1, "name": "おーいお茶", "price": 150}
    else:
        return {"message": "商品がマスタ未登録です"}

# 注文を作成するエンドポイント
@app.post("/orders")
async def create_order(order: dict):
    # ここで注文をデータベースに保存する処理を実装します
    # 仮の応答を返します
    return {"message": "注文が作成されました", "order_id": 1}
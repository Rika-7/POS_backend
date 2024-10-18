from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

# CORSミドルウェアを追加
# これにより、フロントエンド（Next.js）からのリクエストを許可します
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # フロントエンドのURLを指定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"おはよう！": "元気？"}

# 商品の一覧を取得するエンドポイント
@app.get("/items")
async def get_items():
    # ここでデータベースから商品一覧を取得する処理を実装します
    # 仮のデータを返します
    return [
        {"id": 1, "name": "商品A", "price": 100},
        {"id": 2, "name": "商品B", "price": 200},
        {"id": 3, "name": "商品C", "price": 300},
    ]

# 注文を作成するエンドポイント
@app.post("/orders")
async def create_order(order: dict):
    # ここで注文をデータベースに保存する処理を実装します
    # 仮の応答を返します
    return {"message": "注文が作成されました", "order_id": 1}
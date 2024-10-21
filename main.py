from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models

# テーブル作成
Base.metadata.create_all(bind=engine)

# FastAPI instance
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

# データベースへの接続を取得する関数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"おはよう！": "元気？"}

# # 商品の一覧を取得するエンドポイント
# @app.get("/items")
# async def get_items(code: str = Query(None)):
#     # ここでデータベースから商品一覧を取得する処理を実装します
#     # 仮のデータを返します
#     if code == "123":
#         return {"id": 1, "name": "おーいお茶", "price": 150}
#     else:
#         return {"message": "商品がマスタ未登録です"}
    
@app.get("/product/")
def get_product_by_code(code: str, db: Session = Depends(get_db)):
    existing_product = db.query(models.Product).filter(models.Product.code == code).first()
    if existing_product:
        return {
            "id": existing_product.id,
            "name": existing_product.name,
            "price": existing_product.price
        }
    else:
        raise HTTPException(status_code=404, detail="商品がマスタ未登録です")

# 商品を作成するエンドポイント
@app.post("/create_product/")
def create_product(name: str, price: int, code: str, db: Session = Depends(get_db)):
    # Step 1: データベースに商品が存在するか確認
    existing_product = db.query(models.Product).filter(models.Product.code == code).first()
    if existing_product:
        # もし商品が存在する場合は、エラーを返す
        raise HTTPException(status_code=400, detail="Product already exists with this code")

    # Step 2: もし商品が存在しない場合は、新しい商品を作成
    new_product = models.Product(name=name, price=price, code=code)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product



# 注文を作成するエンドポイント
@app.post("/orders")
async def create_order(order: dict):
    # ここで注文をデータベースに保存する処理を実装します
    # 仮の応答を返します
    return {"message": "注文が作成されました", "order_id": 1}
from fastapi import FastAPI, Query, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models
from datetime import datetime
from typing import List, Dict
from models import OrderCreate, OrderItem


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

# 初期データ登録関数
def init_sample_data(db: Session):
    # Check if products already exist
    if db.query(models.Product).first():
        return

    # サンプル商品データ
    sample_products = [
        {"code": "4901085089064", "name": "おーいお茶", "price": 150},
        {"code": "4902430698047", "name": "ソフラン", "price": 300},
        {"code": "4901330571962", "name": "福島産ほうれん草", "price": 188},
        {"code": "4901087728964", "name": "タイガー歯ブラシ青", "price": 200},
        {"code": "4901085192346", "name": "四ツ谷サイダー", "price": 160},
        {"code": "0901255821061", "name": "3種お茶ティーバックセット", "price": 250},
        {"code": "4901201116797", "name": "お茶ティーバックセット", "price": 500},
        {"code": "3282111718211", "name": "インスタントコーヒー", "price": 200},
        {"code": "4911211116717", "name": "インスタントカフェインレスコーヒー", "price": 450},
    ]

    # Insert products
    for product_data in sample_products:
        product = models.Product(**product_data)
        db.add(product)
    
    # Insert tax data
    tax = models.Tax(id=1, code="10", name="10%", percent=10)
    db.add(tax)
    
    db.commit()

@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    try:
        init_sample_data(db)
    finally:
        db.close()

# 商品の一覧を取得するエンドポイント
@app.get("/product/{code}")
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
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    try:
        # 1. Create transaction record
        transaction = models.Transaction(
            datetime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            emp_cd=order.emp_cd,
            store_cd="30",  # 固定値
            pos_no="90",    # 固定値 (モバイルレジ)
            total_amt=0,    # 初期値、後で更新
            ttl_amt_ex_tax=0  # 初期値、後で更新
        )
        db.add(transaction)
        db.flush()  # IDを生成するためにflush

        # 2. Create transaction details
        total_ex_tax = 0
        total_with_tax = 0
        
        for idx, item in enumerate(order.items, 1):
            detail = models.TransactionDetail(
                trd_id=transaction.id,
                dtl_id=idx,
                prd_id=item.product_id,
                prd_code=item.product_code,
                prd_name=item.product_name,
                prd_price=item.product_price,
                tax_cd="10"  # 固定値 (10%税率)
            )
            db.add(detail)
            
            # Calculate totals
            item_total = item.product_price * item.quantity
            total_ex_tax += item_total
            total_with_tax += int(item_total * 1.1)  # 10%税込み計算

        # 3. Update transaction with totals
        transaction.total_amt = total_with_tax
        transaction.ttl_amt_ex_tax = total_ex_tax
        
        db.commit()

        return {
            "message": "注文が作成されました",
            "order_id": transaction.id,
            "total_amount": total_with_tax,
            "total_amount_ex_tax": total_ex_tax
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
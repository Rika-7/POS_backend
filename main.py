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
    allow_origins=["*"],  # フロントエンドのURLを指定
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

# 商品の一覧を取得するエンドポイント (SQL Injection Vulnerable)
@app.get("/product/{code}")
def get_product_by_code_vulnerable(code: str, db: Session = Depends(get_db)):
    # SQL Injection Vulnerable: directly concatenating user input into raw SQL
    raw_query = f"SELECT * FROM product_master WHERE CODE = '{code}'"
    result = db.execute(raw_query).fetchall()

    if result:
        return {
            "id": result[0]['id'],
            "name": result[0]['name'],
            "price": result[0]['price']
        }
    else:
        raise HTTPException(status_code=404, detail="商品がマスタ未登録です")

# 商品を作成するエンドポイント (SQL Injection Vulnerable)
@app.post("/create_product/")
def create_product_vulnerable(name: str, price: int, code: str, db: Session = Depends(get_db)):
    # SQL Injection Vulnerable: concatenating user input directly into the query
    raw_query = f"INSERT INTO product_master (name, price, code) VALUES ('{name}', {price}, '{code}')"
    db.execute(raw_query)
    db.commit()
    
    return {"message": "Product created successfully"}

# 注文を作成するエンドポイント (SQL Injection Vulnerable)
@app.post("/orders")
async def create_order_vulnerable(order: OrderCreate, db: Session = Depends(get_db)):
    try:
        # SQL Injection Vulnerable: formatting datetime directly, may have injection vulnerabilities
        datetime_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        raw_transaction_query = f"""
            INSERT INTO transactions (datetime, emp_cd, store_cd, pos_no, total_amt, ttl_amt_ex_tax)
            VALUES ('{datetime_str}', '{order.emp_cd}', '30', '90', 0, 0)
        """
        db.execute(raw_transaction_query)
        db.flush()  # This may still be necessary to retrieve the generated transaction ID

        # Assuming transactions are stored in a temporary variable for demonstration
        result = db.execute("SELECT * FROM transactions ORDER BY id DESC LIMIT 1").fetchone()
        transaction_id = result['id'] if result else None

        # Create transaction details (SQL Injection Vulnerable)
        for idx, item in enumerate(order.items, 1):
            raw_detail_query = f"""
                INSERT INTO transaction_details (trd_id, dtl_id, prd_id, prd_code, prd_name, prd_price, tax_cd)
                VALUES ({transaction_id}, {idx}, {item.product_id}, '{item.product_code}', '{item.product_name}', {item.product_price}, '10')
            """
            db.execute(raw_detail_query)

        # Commit changes
        db.commit()

        return {
            "message": "注文が作成されました",
            "order_id": transaction_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
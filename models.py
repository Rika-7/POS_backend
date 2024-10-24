# models.py
from sqlalchemy import Column, Integer, String, UniqueConstraint
from database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(13), unique=True, index=True, nullable=False)
    name = Column(String(50), index=True, nullable=False)
    price = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint('code', name='uix_product_code'),
    )

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)  # TRD_ID
    datetime = Column('DATETIME', String(50))
    emp_cd = Column('EMP_CD', String(10))
    store_cd = Column('STORE_CD', String(5))
    pos_no = Column('POS_NO', String(3))
    total_amt = Column('TOTAL_AMT', Integer)
    ttl_amt_ex_tax = Column('TTL_AMT_EX_TAX', Integer)

class TransactionDetail(Base):
    __tablename__ = "transaction_details"

    trd_id = Column('TRD_ID', Integer, primary_key=True)
    dtl_id = Column('DTL_ID', Integer, primary_key=True)
    prd_id = Column('PRD_ID', Integer)
    prd_code = Column('PRD_CODE', String(13))
    prd_name = Column('PRD_NAME', String(50))
    prd_price = Column('PRD_PRICE', Integer)
    tax_cd = Column('TAX_CD', String(2))

class Tax(Base):
    __tablename__ = "tax"

    id = Column(Integer, primary_key=True)
    code = Column(String(2), unique=True)
    name = Column(String(20))
    percent = Column(Integer) 

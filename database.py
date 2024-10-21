import mysql.connector
from mysql.connector import errorcode
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Obtain connection string information from the portal
config = {
  'host':'tech0-db-step4-studentrdb-4.mysql.database.azure.com',
  'user':'tech0gen7student',
  'password':'F4XyhpicGw6P',
  'database':'pos_rr',
  'client_flags': [mysql.connector.ClientFlag.SSL],
  'ssl_ca': '/Users/Rika 1/certificates/DigiCertGlobalRootG2.crt.pem'
}

# SQLAlchemy connection string
DATABASE_URL = f"mysql+mysqlconnector://{config['user']}:{config['password']}@{config['host']}/{config['database']}?ssl_ca={config['ssl_ca']}"

# エンジンを作成
engine = create_engine(DATABASE_URL)

# Session local instance to interact with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for the models
Base = declarative_base()

# データベースに接続する関数
def get_db_connection():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Optional: Maintaining the connection functions for direct connection purposes (using mysql.connector)
# Establishing a direct database connection
# This function will help if you need raw SQL commands or connection for debugging purposes
def get_raw_connection():
    try:
        conn = mysql.connector.connect(**config)
        print("Connection established")
        return conn
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        return None

# データベースへの接続を切断
def close_raw_connection(conn):
    if conn:
        conn.close()
        print("Connection closed")
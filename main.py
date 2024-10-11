from typing import Union
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "POS app"}

@app.get("/items/{item_id}")
def read_item(item_id: int, item_name: Union[str, None] = None):
    return {"item_id": item_id, "item_name": item_name}
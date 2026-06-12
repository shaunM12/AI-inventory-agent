from datetime import datetime

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    store_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    quantity: int = Field(ge=0)
    unit: str = Field(min_length=1)


class StockUpdate(BaseModel):
    delta: int


class StockTransfer(BaseModel):
    product_id: str = Field(min_length=1)
    to_store_id: str = Field(min_length=1)
    quantity: int = Field(gt=0)


class Product(BaseModel):
    product_id: str
    store_id: str
    name: str
    quantity: int
    unit: str
    created_at: datetime
    updated_at: datetime


class Store(BaseModel):
    store_id: str


class TransferResult(BaseModel):
    from_store_id: str
    to_store_id: str
    quantity: int
    source_product: Product
    destination_product: Product

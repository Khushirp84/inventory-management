from pydantic import BaseModel
from typing import Optional

# --- Product Schemas ---
class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    quantity: int
    price: float
    category: Optional[str] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[float] = None
    category: Optional[str] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    quantity: int
    price: float
    category: Optional[str]

    class Config:
        from_attributes = True

# --- Order Schemas ---
class OrderCreate(BaseModel):
    product_id: int
    quantity: int

class OrderResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    status: str

    class Config:
        from_attributes = True
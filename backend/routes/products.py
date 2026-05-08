from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Product
from schemas import ProductCreate, ProductUpdate, ProductResponse
from typing import List

router = APIRouter(prefix="/products", tags=["Products"])

# ✅ CREATE a product
@router.post("/", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    new_product = Product(**product.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

# ✅ GET all products
@router.get("/", response_model=List[ProductResponse])
def get_all_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

# ✅ GET single product by ID
@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# ✅ UPDATE a product
@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, updated: ProductUpdate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in updated.model_dump(exclude_unset=True).items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product

# ✅ DELETE a product
@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"message": f"Product {product_id} deleted ✅"}

# ✅ LOW STOCK ALERT
@router.get("/alerts/low-stock", response_model=List[ProductResponse])
def low_stock_alert(threshold: int = 5, db: Session = Depends(get_db)):
    low_stock = db.query(Product).filter(Product.quantity <= threshold).all()
    return low_stock
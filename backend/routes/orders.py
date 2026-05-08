from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Order, Product
from schemas import OrderCreate, OrderResponse
from typing import List

router = APIRouter(prefix="/orders", tags=["Orders"])

# ✅ CREATE an order
@router.post("/", response_model=OrderResponse)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    # Check if product exists
    product = db.query(Product).filter(Product.id == order.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Check if enough stock
    if product.quantity < order.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough stock. Available: {product.quantity}"
        )

    # Reduce stock
    product.quantity -= order.quantity

    # Create order
    new_order = Order(**order.model_dump())
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order

# ✅ GET all orders
@router.get("/", response_model=List[OrderResponse])
def get_all_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()

# ✅ GET single order
@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

# ✅ UPDATE order status
@router.put("/{order_id}/status", response_model=OrderResponse)
def update_order_status(order_id: int, status: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if status not in ["pending", "completed", "cancelled"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    order.status = status
    db.commit()
    db.refresh(order)
    return order

# ✅ DELETE order
@router.delete("/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    db.delete(order)
    db.commit()
    return {"message": f"Order {order_id} deleted ✅"}
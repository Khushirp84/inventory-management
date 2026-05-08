from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routes import products, orders

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Inventory Management System",
    description="A REST API for managing products and orders",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router)
app.include_router(orders.router)

@app.get("/")
def root():
    return {"message": "Inventory API is running ✅"}
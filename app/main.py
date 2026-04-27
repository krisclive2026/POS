import sys
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.database import init_db, get_db

app = FastAPI(title="POS PoC")

# Initialize DB on startup
init_db()

# Pydantic models
class Item(BaseModel):
    name: str
    price: float
    quantity: int

class Cart(BaseModel):
    items: List[Item]
    total: float

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

static_dir = os.path.join(base_path, 'app', 'static')

# Serve static files
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def read_root():
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.post("/api/checkout")
def checkout(cart: Cart):
    if not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("INSERT INTO sales (total) VALUES (?)", (cart.total,))
        sale_id = cursor.lastrowid
        
        for item in cart.items:
            cursor.execute(
                "INSERT INTO sale_items (sale_id, name, quantity, price) VALUES (?, ?, ?, ?)",
                (sale_id, item.name, item.quantity, item.price)
            )
        db.commit()

    # Mock Printing
    print("\n" + "="*30)
    print("=== CUSTOMER RECEIPT ===")
    print("="*30)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Sale ID: #" + str(sale_id))
    print("-" * 30)
    for item in cart.items:
        print(f"{item.name[:15]:<15} {item.quantity}x @ ${item.price:.2f}")
        print(f"{'':<15}     ${(item.quantity * item.price):.2f}")
    print("-" * 30)
    print(f"TOTAL:           ${cart.total:.2f}")
    print("="*30)
    
    print("\n" + "="*30)
    print("=== VENDOR COPY ===")
    print("="*30)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Sale ID: #" + str(sale_id))
    print("-" * 30)
    for item in cart.items:
        print(f"{item.name[:15]:<15} {item.quantity}x @ ${item.price:.2f}")
        print(f"{'':<15}     ${(item.quantity * item.price):.2f}")
    print("-" * 30)
    print(f"TOTAL:           ${cart.total:.2f}")
    print("="*30 + "\n")

    return {"status": "success", "sale_id": sale_id, "message": "Receipts printed"}

@app.get("/api/sales")
def get_sales():
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM sales ORDER BY timestamp DESC")
        sales = [dict(row) for row in cursor.fetchall()]
    return {"sales": sales}

if __name__ == "__main__":
    import uvicorn
    import multiprocessing
    
    # Required for PyInstaller when using multiprocessing (which uvicorn uses under the hood)
    multiprocessing.freeze_support()
    
    print("Starting POS Server at http://localhost:8000")
    # Pass the actual app object, avoiding string imports which PyInstaller can struggle with
    uvicorn.run(app, host="0.0.0.0", port=8000)


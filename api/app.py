from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse

from api import inventory_service
from api.schemas import Product, ProductCreate, StockTransfer, StockUpdate, Store, TransferResult

app = FastAPI(title="Coffee Shop Inventory API")


@app.exception_handler(inventory_service.ValidationError)
def handle_validation_error(_: Request, exc: inventory_service.ValidationError):
    return JSONResponse(status_code=400, content={"detail": exc.message})


@app.exception_handler(inventory_service.DuplicateProductError)
def handle_duplicate_error(_: Request, exc: inventory_service.DuplicateProductError):
    return JSONResponse(status_code=409, content={"detail": exc.message})


@app.exception_handler(inventory_service.ProductNotFoundError)
def handle_not_found_error(_: Request, exc: inventory_service.ProductNotFoundError):
    return JSONResponse(status_code=404, content={"detail": exc.message})


@app.exception_handler(inventory_service.StoreNotFoundError)
def handle_store_not_found(_: Request, exc: inventory_service.StoreNotFoundError):
    return JSONResponse(status_code=404, content={"detail": exc.message})


@app.exception_handler(inventory_service.StockConflictError)
def handle_stock_conflict(_: Request, exc: inventory_service.StockConflictError):
    return JSONResponse(status_code=409, content={"detail": exc.message})


@app.exception_handler(inventory_service.PersistenceError)
def handle_persistence_error(_: Request, exc: inventory_service.PersistenceError):
    return JSONResponse(status_code=500, content={"detail": exc.message})


@app.get("/stores", response_model=list[Store])
def get_stores():
    return inventory_service.list_stores()


@app.get("/inventory", response_model=list[Product])
def get_inventory(store_id: str | None = Query(default=None)):
    return inventory_service.list_inventory(store_id=store_id)


@app.get("/stores/{store_id}/inventory", response_model=list[Product])
def get_store_inventory(store_id: str):
    return inventory_service.get_store_inventory(store_id)


@app.post("/inventory", response_model=Product, status_code=201)
def post_inventory(payload: ProductCreate):
    return inventory_service.create_product(payload)


@app.patch("/inventory/{product_id}", response_model=Product)
def patch_inventory(product_id: str, payload: StockUpdate):
    return inventory_service.update_stock(product_id, payload)


@app.delete("/inventory/{product_id}", response_model=Product)
def delete_inventory(product_id: str):
    return inventory_service.delete_product(product_id)


@app.post("/inventory/transfer", response_model=TransferResult)
def post_inventory_transfer(payload: StockTransfer):
    return inventory_service.transfer_stock(payload)


@app.get("/inventory/alerts", response_model=list[Product])
def get_inventory_alerts(store_id: str | None = Query(default=None)):
    return inventory_service.get_low_stock_alerts(store_id=store_id)

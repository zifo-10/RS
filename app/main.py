from fastapi import FastAPI

from app.routes import items, transactions, similar

app = FastAPI()

app.include_router(items.router, prefix="/api")
app.include_router(transactions.router, prefix="/api")
app.include_router(similar.router, prefix="/api")

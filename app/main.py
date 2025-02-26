from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import items, transactions, similar, llm

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(items.router, prefix="/api")
app.include_router(transactions.router, prefix="/api")
app.include_router(similar.router, prefix="/api")
app.include_router(llm.router, prefix="/api")

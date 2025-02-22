# app/routes/transactions.py
from fastapi import APIRouter

from app.dependencies import transaction_service
from app.models.transactions import Transaction

router = APIRouter()


@router.post("/transactions/")
async def create_transaction(transaction: Transaction):
    transaction_id = transaction_service().create_transaction(transaction)
    return {"transaction_id": transaction_id}

# app/routes/items.py
from typing import Dict

from fastapi import APIRouter
from pyobjectID import PyObjectId

from app.dependencies import item_service
from app.models.item import Item

router = APIRouter()


@router.post("/items/")
async def create_item(item: Item) -> Dict[str, str]:
    # Insert item into MongoDB
    inserted_id = item_service().insert(item)
    return {"item_id": str(inserted_id)}


@router.get("/items/{item_id}")
async def get_item(item_id: PyObjectId):
    # Get item from MongoDB
    item = item_service().get_item(item_id)
    return item

# app/routes/items.py
from fastapi import APIRouter
from pyobjectID import PyObjectId

from app.dependencies import insert_service
from app.models.item import Item

router = APIRouter()


@router.post("/items/")
async def create_item(item: Item):
    # Insert item into MongoDB
    inserted_id = insert_service().insert(item)
    return {"id": inserted_id}


@router.get("/items/{item_id}")
async def get_item(item_id: PyObjectId):
    # Get item from MongoDB
    item = insert_service().get_item(item_id)
    return {"item": item}

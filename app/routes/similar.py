# app/routes/similar.py
from fastapi import APIRouter
from pyobjectID import PyObjectId

from app.dependencies import similar_service
from app.models.similarity_search import SimilaritySearch

router = APIRouter()


@router.post("/search")
def search_items(query: SimilaritySearch):
    items = similar_service().search(query)
    return {"items": items}


@router.get("/related_transaction/{item_id}")
async def get_related_items(item_id: PyObjectId):
    related_items = similar_service().get_related_transaction(item_id)
    return {"related_items": related_items}


@router.post("/web_search/{item_id}")
async def search_web(item_id: PyObjectId):
    related_items = similar_service().web_search(item_id)
    return {"related_items": related_items}

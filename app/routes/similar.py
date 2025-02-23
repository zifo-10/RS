# app/routes/similar.py
from typing import Dict, List

from fastapi import APIRouter
from pyobjectID import PyObjectId

from app.dependencies import similar_service
from app.models.item import GetItem
from app.models.similarity_search import SimilaritySearch

router = APIRouter()


@router.post("/search")
def search_items(query: SimilaritySearch) -> Dict[str, List[GetItem]]:
    """
    Search for items similar to the provided query.

    :param query: The query to search for.
    :return: Dictionary containing the search results.
    """
    items = similar_service().search(query)
    return {"items": items}


@router.get("/related_transaction/{item_id}")
async def get_related_items(item_id: PyObjectId) -> Dict[str, List]:
    related_items = similar_service().get_related_transaction(item_id)
    return {"items": related_items}


@router.get("/web_search/{item_id}")
async def search_web(item_id: PyObjectId):
    related_items = similar_service().web_search(item_id)
    return {"items": related_items}

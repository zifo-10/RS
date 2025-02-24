from bson import ObjectId

from app.core.embed import CohereClient
from app.core.web_search import WebSearch
from app.database.mongo import Mongo
from app.database.qdrant import VectorDBClient
from app.models.item import GetItem
from app.models.similarity_search import SimilaritySearch
from app.services.item_service import ItemService


class SimilarService:
    def __init__(self, mongo: Mongo, cohere: CohereClient,
                 vectordb: VectorDBClient, web_search_service: WebSearch,
                 item_service: ItemService):
        self.mongo = mongo
        self.cohere = cohere
        self.vectordb = vectordb
        self.web_search_service = web_search_service
        self.item_service = item_service

    def get_related_transaction(self, item_id: ObjectId):
        pipeline = [
            # Step 1: Find transactions that contain the selected item
            {"$match": {"items": item_id}},

            # Step 2: Unwind the items array
            {"$unwind": "$items"},

            # Step 3: Exclude the selected item
            {"$match": {"items": {"$ne": item_id}}},

            # Step 4: Group by item ID and count occurrences
            {"$group": {"_id": "$items", "count": {"$sum": 1}}},

            # Step 5: Sort by frequency (most frequently bought together items first)
            {"$sort": {"count": -1}},

            # Step 6: Limit results to top 10 (if available)
            {"$limit": 10}
        ]

        # Run the aggregation
        related_items = list(self.mongo.aggregate(collection="transactions", pipeline=pipeline))

        items_details = []
        for item in related_items:
            item_details = self.item_service.get_item(item["_id"])
            items_details.append(item_details)
        return items_details

    def search(self, query: SimilaritySearch) -> list[GetItem]:
        # Define the search query embedding
        embedding = self.cohere.embed_text(
            texts=[query.query],
            model="embed-multilingual-light-v3.0",
            input_type="search_query",
            embedding_types=["float"]
        )

        # Detect language of the query and select the collection accordingly
        if '\u0600' <= query.query[0] <= '\u06FF' or '\u0750' <= query.query[0] <= '\u077F' or '\u08A0' <= query.query[
            0] <= '\u08FF':
            collection_name = "items_ar"
        else:
            collection_name = "items_en"

        # Perform the search to get the sorted vector IDs
        search_vector = self.vectordb.search_vector(
            query_vector=embedding,
            collection_name=collection_name,
            top_k=query.limit,
            filters=query.filters,
            score_threshold=query.score_threshold
        )

        # Extract and prepare IDs from search_vector in the sorted order
        ids_to_search = [ObjectId(item) for item in search_vector]

        # Fetch the items from MongoDB in bulk using $in to get the documents
        items = self.item_service.get_items(ids_to_search)

        return items

    def web_search(self, item_id: ObjectId):
        item = self.mongo.find_one(collection="items", query={"_id": item_id})
        web_search_results = self.web_search_service.search(f"{item['name']}")
        return web_search_results

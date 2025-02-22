from bson import ObjectId

from app.database.mongo import Mongo
from app.database.qdrant import VectorDBClient
from app.models.item import GetItem
from app.models.similarity_search import SimilaritySearch
from app.core.embed import CohereClient
from app.core.web_search import WebSearch


class SimilarService:
    def __init__(self, mongo: Mongo, cohere: CohereClient, vectordb: VectorDBClient, web_search_service: WebSearch):
        self.mongo = mongo
        self.cohere = cohere
        self.vectordb = vectordb
        self.web_search_service = web_search_service

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

            # Step 6: Limit results (optional, e.g., top 5)
            {"$limit": 5}
        ]

        # Run the aggregation
        related_items = list(self.mongo.aggregate(collection="transactions", pipeline=pipeline))
        for item in related_items:
            item["_id"] = str(item["_id"])
        return related_items

    def search(self, query: SimilaritySearch):
        # Define the search query
        embedding = self.cohere.embed_text(texts=[query.query],
                                           model="embed-multilingual-light-v3.0",
                                           input_type="search_query",
                                           embedding_types=["float"])
        search_vector = self.vectordb.search_vector(query_vector=embedding,
                                                    collection_name="items",
                                                    top_k=query.limit,
                                                    filters=query.filters)
        return search_vector

    def web_search(self, item_id: ObjectId):
        item = GetItem(**self.mongo.find_one(collection="items", query={"_id": item_id}))
        web_search_results = self.web_search_service.search(f"{item.name}")
        return web_search_results
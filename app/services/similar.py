from bson import ObjectId

from app.core.embed import CohereClient
from app.core.web_search import WebSearch
from app.database.mongo import Mongo
from app.database.qdrant import VectorDBClient
from app.models.item import GetItem
from app.models.similarity_search import SimilaritySearch


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

            # Step 6: Limit results to top 10 (if available)
            {"$limit": 10}
        ]

        # Run the aggregation
        related_items = list(self.mongo.aggregate(collection="transactions", pipeline=pipeline))

        items_details = []
        for item in related_items:
            item_detail = self.mongo.find_one(collection="items", query={"_id": ObjectId(item["_id"])})
            item_detail["image_path"] = f"static/{item_detail['name']}.jpg"
            # Append item details
            items_details.append(GetItem(**item_detail))

        return items_details

    def search(self, query: SimilaritySearch) -> list[GetItem]:
        # Define the search query
        embedding = self.cohere.embed_text(
            texts=[query.query],
            model="embed-multilingual-light-v3.0",
            input_type="search_query",
            embedding_types=["float"]
        )

        # Perform the search to get the sorted vector IDs
        search_vector = self.vectordb.search_vector(
            query_vector=embedding,
            collection_name="items",
            top_k=query.limit,
            filters=query.filters,
            score_threshold=query.score_threshold
        )

        # Extract IDs from search_vector in the sorted order
        ids_to_search = [ObjectId(item) for item in search_vector]

        # Fetch the items from MongoDB in bulk using $in to get the documents
        items = self.mongo.find_many(collection="items", query={"_id": {"$in": ids_to_search}})

        # Create a dictionary to map Mongo documents by their _id for quick access
        items_dict = {str(item["_id"]): item for item in items}

        # Prepare the result list, preserving the order of search_vector
        search_result = [
            GetItem(**items_dict[str(ObjectId(item))],
                    image_path=f"static/{items_dict[str(ObjectId(item))]['name']}.jpg")
            for item in search_vector
            if str(ObjectId(item)) in items_dict  # Only add if item exists in MongoDB
        ]

        return search_result

    def web_search(self, item_id: ObjectId):
        item = self.mongo.find_one(collection="items", query={"_id": item_id})
        web_search_results = self.web_search_service.search(f"{item['name']}")
        return web_search_results

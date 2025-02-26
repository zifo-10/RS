from typing import Any

from bson import ObjectId
from scipy.spatial.distance import cosine

from app.clean_text import clean_arabic_text
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

    def mongo_full_text_search(self, query: str, filter: dict = None) -> list[GetItem]:
        mongo_search_result = self.mongo.full_text_search(collection="items", query=query, filter=filter)
        result_list = []
        for item in mongo_search_result:
            # item["image"] = self.item_service.read_image(item["name_en"])
            item = GetItem(**item)
            result_list.append(item)
        return result_list

    def generate_embedding(self, text: str):
        embedding = self.cohere.embed_text(
            texts=[text],
            model="embed-multilingual-light-v3.0",
            input_type="search_query",
            embedding_types=["float"]
        )
        return embedding

    def rerank_documents(self, query: str, documents: list[GetItem], is_arabic: bool) -> list:
        """Re-rank documents based on their embedding similarity to the query."""
        # Generate the embedding for the query
        query_embedding = self.generate_embedding(query)

        documents_with_sim = []

        for doc in documents:
            # Depending on the query language, choose Arabic or English fields
            if is_arabic:
                # Arabic query: use Arabic fields
                document_text = (f"name: {doc.name_ar} description: {doc.description_ar} "
                                 f"color: {doc.color_ar}")
            else:
                # English query: use English fields
                document_text = (f"name: {doc.name_en} description: {doc.description_en} "
                                 f"color: {doc.color_en}")

            # Generate the embedding for the document text
            document_embedding = self.generate_embedding(document_text)

            # Compute cosine similarity with the query embedding
            similarity = 1 - cosine(query_embedding, document_embedding)

            documents_with_sim.append((doc, similarity))

        # Sort the documents by similarity in descending order
        documents_with_sim.sort(key=lambda x: x[1], reverse=True)

        # Return the documents sorted by similarity
        return [doc for doc, _ in documents_with_sim]

    def similarity_search(self, query: SimilaritySearch, is_arabic: bool):

        query_embedding = self.generate_embedding(query.query)
        # Perform the search to get the sorted vector IDs
        search_vector = self.vectordb.search_vector(
            query_vector=query_embedding,
            collection_name="items_ar" if is_arabic else "items_en",
            top_k=query.limit,
            score_threshold=query.score_threshold
        )
        # Extract and prepare IDs from search_vector in the sorted order
        ids_to_search = [ObjectId(item) for item in search_vector]
        # Fetch the items from MongoDB in bulk using $in to get the documents
        items = self.item_service.get_items(ids_to_search)
        return items

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

    def search(self, query: SimilaritySearch) -> dict[str, list[GetItem] | list[Any] | list]:
        # Detect language of the query and set flag for Arabic or English
        is_arabic = False
        if '\u0600' <= query.query[0] <= '\u06FF' or '\u0750' <= query.query[0] <= '\u077F' or '\u08A0' <= query.query[
            0] <= '\u08FF':
            is_arabic = True

        # First, perform the MongoDB full-text search to get the initial results
        cleaned_query = clean_arabic_text(query.query)
        reranked_documents = []
        similar_result = []
        full_text_search_results = self.mongo_full_text_search(cleaned_query, filter=query.filters)[:query.limit]
        if full_text_search_results:
            # Rerank documents based on embedding similarity, depending on query language
            reranked_documents = self.rerank_documents(query.query, full_text_search_results, is_arabic)

        if len(full_text_search_results) < query.limit:
            new_limit = query.limit - len(full_text_search_results)
            query.limit = new_limit
            similar_result = self.similarity_search(query, is_arabic)

            # Remove items in reranked_documents from similar_result
            similar_result = [item for item in similar_result if item not in reranked_documents]

        results = {
            "results": reranked_documents,
            "related_results": similar_result
        }
        return results

    def web_search(self, item_id: ObjectId) -> dict[str, list[dict[str, Any]] | Any]:
        item = GetItem(**self.mongo.find_one(collection="items", query={"_id": item_id}))
        query_en = f"{item.name_en} {item.color}"
        web_search_results_en = self.web_search_service.search(query_en)
        return web_search_results_en

import uuid

from qdrant_client import QdrantClient
from qdrant_client import models
from qdrant_client.models import PointStruct


class VectorDBClient:
    def __init__(self, host: str, port: int):
        self.client = QdrantClient(url=host, port=port)

    def create_collection(self):
        self.client.create_collection(
            collection_name="items_en",
            vectors_config=models.VectorParams(
                size=384,
                distance=models.Distance.COSINE),
        )
    def insert_vector(self, vector: list, payload: dict, collection_name: str):
        point_id = str(uuid.uuid4())
        self.client.upsert(
            collection_name=collection_name,
            points=[
                PointStruct(id=point_id, vector=vector, payload=payload)
            ],
        )
        return point_id

    def search_vector(self, query_vector: list, collection_name: str,
                      score_threshold: float, top_k: int,
                      filters: dict = None):
        must = []
        if filters:
            for key, value in filters.items():
                must.append(
                    models.FieldCondition(
                        key=key,
                        match=models.MatchValue(
                            value=value,
                        ),
                    )
                )
        results = self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=top_k,
            query_filter=models.Filter(
                must=must
            ),
            search_params=models.SearchParams(exact=True),
            score_threshold=score_threshold
        )
        # Sort results by the score in descending order
        sorted_results = sorted(results, key=lambda x: x.score, reverse=True)

        ids_list = []
        for result in sorted_results:
            mongo_id = result.model_dump()['payload']['id']
            ids_list.append(mongo_id)

        return ids_list


# VectorDBClient(host="http://172.105.247.6", port=6333).create_collection()
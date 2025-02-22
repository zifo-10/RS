import uuid
from qdrant_client import models
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct


class VectorDBClient:
    def __init__(self, host: str, port: int):
        self.client = QdrantClient(url=host, port=port)

    def insert_vector(self, vector: list, payload: dict, collection_name: str):
        point_id = str(uuid.uuid4())
        self.client.upsert(
            collection_name=collection_name,
            points=[
                PointStruct(id=point_id, vector=vector, payload=payload)
            ],
        )
        return point_id

    def search_vector(self, query_vector: list, collection_name: str, top_k: int, filters: dict = None):
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
            score_threshold=0.0
        )
        ids_list = []
        for result in results:
            mongo_id = result.model_dump()['payload']['id']
            ids_list.append(mongo_id)
        return list(set(ids_list))

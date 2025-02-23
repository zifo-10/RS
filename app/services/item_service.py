from bson import ObjectId

from app.core.embed import CohereClient
from app.database.mongo import Mongo
from app.database.qdrant import VectorDBClient
from app.models.item import Item, GetItem


class InsertService:
    def __init__(self, mongo: Mongo, cohere: CohereClient, vectordb: VectorDBClient):
        self.mongo = mongo
        self.cohere = cohere
        self.vectordb = vectordb

    def insert(self, data: Item) -> str:
        """
        Insert the provided data into the MongoDB database.

        This method inserts the provided data into the MongoDB database
        and returns the ID of the inserted document.

        :param data: The data to insert.
        :return: The ID of the inserted document.
        """
        # Insert the data into the database
        result = self.mongo.insert(collection="items", data=data.model_dump())
        embedding = self.cohere.embed_text(texts=[data.description],
                                           model="embed-multilingual-light-v3.0",
                                           input_type="search_query",
                                           embedding_types=["float"])
        # Insert the vector into the vector database
        self.vectordb.insert_vector(vector=embedding,
                                    payload={"id": str(result.inserted_id),
                                             "color": data.color,
                                             "material": data.material,
                                             "category": data.category,
                                             "price": data.price},
                                    collection_name="items")
        return str(result.inserted_id)

    def get_item(self, item_id: ObjectId) -> GetItem:
        """
        Get the item from the MongoDB database.

        This method retrieves the item with the provided ID from the MongoDB database.

        :param item_id: The ID of the item to retrieve.
        :return: The retrieved item.
        """
        # Retrieve the item from the database
        item = GetItem(**self.mongo.find_one(collection="items", query={"_id": item_id}))
        return item

from pymongo import MongoClient
from pymongo.results import InsertOneResult


class Mongo:
    def __init__(self, uri: str, db_name: str):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    def insert(self, collection: str, data: dict) -> InsertOneResult:
        return self.db[collection].insert_one(data)

    def aggregate(self, collection: str, pipeline: list) -> list:
        return list(self.db[collection].aggregate(pipeline))

    def find_one(self, collection: str, query: dict) -> dict:
        return self.db[collection].find_one(query)

    def find_many(self, collection: str, query: dict) -> list:
        return list(self.db[collection].find(query))

    def full_text_search(self, collection: str, query: str, filter: dict = None) -> list:
        # Merge the query with the filter dictionary if filter is provided
        query_dict = {"$text": {"$search": query}}

        if filter:
            query_dict.update(filter)  # Merge filter into query_dict

        # Perform the search
        return list(self.db[collection].find(query_dict))

    def get_messages(self, collection: str, query: dict, limit: int) -> list:
        return list(
            self.db[collection].find(query).sort("created_at", -1).limit(limit)
        )

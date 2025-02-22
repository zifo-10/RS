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
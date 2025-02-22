from app.database.mongo import Mongo
from app.models.transactions import Transaction


class TransactionService:
    def __init__(self, mongo: Mongo):
        self.mongo = mongo

    def create_transaction(self, transaction: Transaction) -> str:
        """
        Create a new transaction in the MongoDB database.

        This method creates a new transaction in the MongoDB database
        and returns the ID of the created transaction.

        :param transaction: The transaction to create.
        :return: The ID of the created transaction.
        """
        result = self.mongo.insert(collection="transactions", data=transaction.model_dump())
        return str(result.inserted_id)

# app/models/transaction.py
from typing import List

import pyobjectID
from pydantic import BaseModel


class Transaction(BaseModel):
    user_id: pyobjectID.PyObjectId
    items: List[pyobjectID.PyObjectId]

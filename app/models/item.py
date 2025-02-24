# app/models/item.py
from pydantic import BaseModel, Field
from pyobjectID import MongoObjectId

class Item(BaseModel):
    name: str
    description_ar: str
    description_en: str
    color: str
    price: float
    material: str
    related_items: list
    category: str


class GetItem(Item):
    id: MongoObjectId = Field(alias="_id")
    image: bytes


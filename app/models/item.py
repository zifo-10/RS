# app/models/item.py
from typing import Optional

from pydantic import BaseModel, Field
from pyobjectID import MongoObjectId


class Item(BaseModel):
    name_ar: str
    name_en: str
    description_ar: str
    description_en: str
    color_ar: str
    color_en: str
    material: str
    price: float


class GetItem(Item):
    id: MongoObjectId = Field(alias="_id")
    image: Optional[bytes] = Field(default=None)

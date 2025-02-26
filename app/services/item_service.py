import base64
import os

from bson import ObjectId

from app.clean_text import clean_arabic_text
from app.core.embed import CohereClient
from app.database.mongo import Mongo
from app.database.qdrant import VectorDBClient
from app.models.item import Item, GetItem

products = [
    {
        "name_ar": "لباس سلامة",
        "name_en": "Safety Vest",
        "description_ar": "لباس يعكس الضوء يستخدم في مواقع البناء لضمان السلامة.",
        "description_en": "A reflective vest used at construction sites for safety.",
        "color_en": "orange",
        "color_ar": "برتقالي",
        "material": "polyester",
        "price": 75.00
    },
    {
        "name_ar": "خوذة أمان",
        "name_en": "Safety Helmet",
        "description_ar": "خوذة واقية للرأس تستخدم في مواقع البناء لحماية العمال.",
        "description_en": "A protective helmet used at construction sites to protect workers.",
        "color_en": "yellow",
        "color_ar": "أصفر",
        "material": "hard plastic",
        "price": 120.00
    },
    {
        "name_ar": "نظارات حماية",
        "name_en": "Safety Glasses",
        "description_ar": "نظارات واقية تستخدم لحماية العينين أثناء العمل.",
        "description_en": "Protective glasses used to shield the eyes while working.",
        "color_en": "clear",
        "color_ar": "شفاف",
        "material": "plastic",
        "price": 60.00
    },
    {
        "name_ar": "قفازات عازلة",
        "name_en": "Insulated Gloves",
        "description_ar": "قفازات توفر الحماية ضد الكهرباء والمواد الكيميائية.",
        "description_en": "Gloves that provide protection against electricity and chemicals.",
        "color_en": "yellow",
        "color_ar": "أصفر",
        "material": "rubber",
        "price": 90.00
    },
    {
        "name_ar": "أشرطة قياس",
        "name_en": "Measuring Tape",
        "description_ar": "شريط مرن يستخدم لقياس المسافات بدقة.",
        "description_en": "A flexible tape used for accurately measuring distances.",
        "color_en": "yellow",
        "color_ar": "أصفر",
        "material": "metal, plastic",
        "price": 50.00
    },
    {
        "name_ar": "مرشح هواء صناعي",
        "name_en": "Industrial Air Filter",
        "description_ar": "مرشح يستخدم لتنقية الهواء من الغبار والملوثات في مواقع العمل.",
        "description_en": "A filter used to purify air from dust and pollutants at work sites.",
        "color_en": "white",
        "color_ar": "أبيض",
        "material": "synthetic fibers",
        "price": 500.00
    }
]


class ItemService:
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
        for product in products:
            print(product)
            data = Item(**product)
            data.name_ar = clean_arabic_text(data.name_ar)
            # Insert the data into the database
            result = self.mongo.insert(collection="items", data=data.model_dump())

            embed_sentence_ar = f"{data.name_ar} {data.description_ar}"
            embedding_ar = self.cohere.embed_text(texts=[embed_sentence_ar],
                                                  model="embed-multilingual-light-v3.0",
                                                  input_type="search_query",
                                                  embedding_types=["float"])
            embed_sentence_en = f"{data.name_en} {data.description_en}"
            embedding_en = self.cohere.embed_text(texts=[embed_sentence_en],
                                                  model="embed-multilingual-light-v3.0",
                                                  input_type="search_query",
                                                  embedding_types=["float"])
            # Insert the vector into the vector database
            self.vectordb.insert_vector(vector=embedding_ar,
                                        payload={"id": str(result.inserted_id)},
                                        collection_name="items_ar")
            self.vectordb.insert_vector(vector=embedding_en,
                                        payload={"id": str(result.inserted_id)},
                                        collection_name="items_en")
        return "str(result.inserted_id)"

    @staticmethod
    def read_image(image_name: str):
        """Search for an image file in STATIC_FOLDER with any extension."""
        for file in os.listdir('static'):
            if file.startswith(image_name + "."):
                image_path = os.path.join('static', file)
                # Read image bytes
                if image_path:
                    with open(image_path, "rb") as img_file:
                        image_bytes = img_file.read()
                else:
                    image_bytes = None
                encoded_images = base64.b64encode(image_bytes).decode("utf-8")
                return encoded_images

    def get_item(self, item_id: ObjectId) -> GetItem:
        """
        Get the item from the MongoDB database.

        This method retrieves the item with the provided ID from the MongoDB database.

        :param item_id: The ID of the item to retrieve.
        :return: The retrieved item.
        """
        # Retrieve the item from the database
        item = self.mongo.find_one(collection="items", query={"_id": item_id})
        # Add image bytes to response
        item["image"] = self.read_image(item["name_en"])
        return GetItem(**item)

    def get_items(self, items_ids: list[ObjectId]) -> list[GetItem]:
        """
        Get the items from the MongoDB database in the same order as items_ids.

        :param items_ids: The IDs of the items to retrieve.
        :return: The retrieved items in the same order.
        """
        pipeline = [
            {"$match": {"_id": {"$in": items_ids}}},
            {"$addFields": {"sortIndex": {"$indexOfArray": [items_ids, "$_id"]}}},
            {"$sort": {"sortIndex": 1}}
        ]

        items = self.mongo.aggregate(collection="items", pipeline=pipeline)

        result_list = []
        for item in items:
            # item["image"] = self.read_image(item["name_en"])
            item = GetItem(**item)
            result_list.append(item)
        return result_list

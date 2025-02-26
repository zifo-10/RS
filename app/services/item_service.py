import base64
import os

from bson import ObjectId

from app.clean_text import clean_arabic_text
from app.core.embed import CohereClient
from app.database.mongo import Mongo
from app.database.qdrant import VectorDBClient
from app.models.item import Item, GetItem

products = [
    # Similar Nails (مسامير)
    {
        "name_ar": "مسمار حديدي",
        "name_en": "Iron Nail",
        "description_ar": "مسمار مصنوع من الحديد، يستخدم في تثبيت الأخشاب والمواد المختلفة.",
        "description_en": "An iron nail used for fastening wood and other materials.",
        "color": "gray",
        "material": "iron",
        "price": 5.00,  # price in EGP
    },
    {
        "name_ar": "مسمار فولاذي",
        "name_en": "Steel Nail",
        "description_ar": "مسمار فولاذي مقاوم للصدأ، مثالي للبناء والتشطيبات.",
        "description_en": "A stainless steel nail, ideal for construction and finishing.",
        "color": "silver",
        "material": "steel",
        "price": 6.50,  # price in EGP
    },
    {
        "name_ar": "مسمار سقف",
        "name_en": "Roofing Nail",
        "description_ar": "مسمار ذو رأس عريض يستخدم في تثبيت ألواح الأسقف.",
        "description_en": "A nail with a wide head used for securing roofing sheets.",
        "color": "black",
        "material": "steel",
        "price": 7.00,  # price in EGP
    },
    {
        "name_ar": "مسمار خرساني",
        "name_en": "Concrete Nail",
        "description_ar": "مسمار شديد الصلابة يستخدم في تثبيت المواد في الخرسانة.",
        "description_en": "An extremely tough nail used for securing materials into concrete.",
        "color": "gray",
        "material": "steel",
        "price": 8.00,  # price in EGP
    },
    {
        "name_ar": "رمل بناء",
        "name_en": "Construction Sand",
        "description_ar": "رمل ناعم يستخدم في أعمال البناء والخرسانة لتوفير متانة وقوة إضافية.",
        "description_en": "Fine sand used in construction and concrete work to provide additional durability and strength.",
        "color": "yellow",
        "material": "sand",
        "price": 20.00,  # price in EGP
    },
    {
        "name_ar": "زلط ناعم",
        "name_en": "Fine Gravel",
        "description_ar": "زلط ناعم يستخدم في الخرسانة الخفيفة وأعمال التشطيب.",
        "description_en": "Fine gravel used in lightweight concrete and finishing work.",
        "color": "gray",
        "material": "gravel",
        "price": 15.00,  # price in EGP
    },
    {
        "name_ar": "زلط خشن",
        "name_en": "Coarse Gravel",
        "description_ar": "زلط بحجم كبير يستخدم في الخرسانة الثقيلة وأساسات البناء.",
        "description_en": "Large-sized gravel used in heavy concrete and building foundations.",
        "color": "gray",
        "material": "gravel",
        "price": 18.00,  # price in EGP
    },
    {
        "name_ar": "مطرقة يدوية",
        "name_en": "Hand Hammer",
        "description_ar": "مطرقة يدوية متعددة الاستخدامات مصنوعة من الفولاذ مع مقبض خشبي.",
        "description_en": "A versatile hand hammer made of steel with a wooden handle.",
        "color": "silver",
        "material": "steel, Wood",
        "price": 30.00,  # price in EGP
    },
    {
        "name_ar": "مطرقة مطاطية",
        "name_en": "Rubber Mallet",
        "description_ar": "مطرقة ذات رأس مطاطي تستخدم في الأعمال التي تحتاج إلى ضربات غير مؤذية.",
        "description_en": "A hammer with a rubber head used for non-damaging strikes.",
        "color": "black",
        "material": "rubber",
        "price": 25.00,  # price in EGP
    },
    {
        "name_ar": "إسمنت",
        "name_en": "Cement",
        "description_ar": "مادة رابطة تستخدم في البناء لربط المواد معًا وتشكيل الخرسانة.",
        "description_en": "A binding material used in construction to hold materials together and form concrete.",
        "color": "gray",
        "material": "cement",
        "price": 50.00,  # price in EGP
    },
    {
        "name_ar": "طوب",
        "name_en": "Bricks",
        "description_ar": "وحدات بناء مصنوعة من الطين أو الخرسانة تستخدم في تشييد الجدران والمباني.",
        "description_en": "Building units made of clay or concrete used for constructing walls and buildings.",
        "color": "red",
        "material": "clay",
        "price": 3.00,  # price in EGP
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

        return [GetItem(**item) for item in items]

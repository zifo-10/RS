from app.config import config
from app.core.embed import CohereClient
from app.core.llm import LLM
from app.core.web_search import WebSearch
from app.database.mongo import Mongo
from app.database.qdrant import VectorDBClient
from app.services.item_service import ItemService
from app.services.llm_service import LLMService
from app.services.similar import SimilarService
from app.services.transaction_service import TransactionService


def get_qdrant_client():
    return VectorDBClient(host=config.VECTOR_DB_URI,
                          port=config.VECTOR_DB_PORT)


def get_llm():
    return LLM(api_key=config.OPEN_AI_API)


def get_cohere_client():
    return CohereClient(api_key=config.COHERE_API_KEY)


def get_mongo_client():
    return Mongo(uri=config.MONGO_URI, db_name=config.MONGO_DB_NAME)


def get_llm_service():
    return LLMService(llm=LLM(api_key=config.OPEN_AI_API),
                      search_service=similar_service(),
                      web_search_service=get_web_search_service(),
                      item_service=item_service())


def get_web_search_service():
    return WebSearch(api_key=config.TAVILYAPI_KEY)


def item_service():
    return ItemService(mongo=get_mongo_client(),
                       cohere=get_cohere_client(),
                       vectordb=get_qdrant_client())


def transaction_service():
    return TransactionService(mongo=get_mongo_client())


def similar_service():
    return SimilarService(mongo=get_mongo_client(),
                          cohere=get_cohere_client(),
                          vectordb=get_qdrant_client(),
                          web_search_service=get_web_search_service(),
                          item_service=item_service())

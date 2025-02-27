from typing import Optional

from bson import ObjectId

from app.core.llm import LLM
from app.core.web_search import WebSearch
from app.models.prompt import Prompt
from app.models.similarity_search import SimilaritySearch
from app.services.item_service import ItemService
from app.services.similar import SimilarService


class LLMService:
    def __init__(self, llm: LLM,
                 search_service: SimilarService,
                 web_search_service: WebSearch,
                 item_service: ItemService
                 ):
        self.llm = llm
        self.search_service = search_service
        self.web_search_service = web_search_service
        self.item_service = item_service

    def generate_response(self, system: str, user: str):
        """Returns a generator to enable streaming responses."""
        result = self.llm.generate_response(system, user)
        return result

    def search_items(self, query: SimilaritySearch) -> dict:
        """Searches for similar items and returns search results."""
        result = self.search_service.search(query)

        # Use list comprehension to extract results and exclude the 'image' field
        full_text_results = [item.model_dump(exclude={'image'}) for item in result["results"]]
        similar_items = [item.model_dump(exclude={'image'}) for item in result["related_results"]]

        return {
            "results": full_text_results,
            "related_results": similar_items
        }

    def _generate_system_message(self, system) -> str:
        """Generates the system instruction for the AI model."""
        return system

    def _generate_user_message(
            self, query: str, full_text_search_result: list, similar_items: list,
            lang: str, user: str,
            chat_history: Optional[list] = None,
            web_search_result: Optional[list] = None
    ) -> str:
        """Creates a user message prompt for the AI model."""
        formated_user = (user.replace("{query}", query)
                         .replace("{lang}", lang)
                         .replace("{chat_history}", str(chat_history))
                         .replace("{full_text_search_result}", str(full_text_search_result))
                         .replace("{similar_items}", str(similar_items))
                         .replace("{web_search_result}", str(web_search_result)))
        return formated_user

    def chat(
            self, query: str, limit: int = 10, score_threshold: float = 0.3, filters: Optional[dict] = None,
            conversation_id: Optional[str] = None,
            search: bool = True
    ):
        if not conversation_id:
            conversation_id = self.item_service.create_conversation()
        chat_history = self.item_service.get_messages(ObjectId(conversation_id))
        new_query = query + " " + chat_history[0].question if chat_history else query
        lang = "en"
        if '\u0600' <= query[0] <= '\u06FF' or '\u0750' <= query[0] <= '\u077F' or '\u08A0' <= query[
            0] <= '\u08FF':
            lang = "ar"
        # Retrieve knowledge base results
        knowledge_base = self.search_items(
            query=SimilaritySearch(query=new_query, limit=limit, score_threshold=score_threshold, filters=filters)
        )
        print("knowledge_base***************", knowledge_base)
        web_search_results = self.web_search_service.search(query) if search else {"results": []}
        # Generate system and user messages
        prompt = Prompt(**self.item_service.get_prompt(prompt_id=ObjectId("67c045cf1eb68369147527c0")))
        system_message = self._generate_system_message(prompt.system)
        user_message = self._generate_user_message(
            query=query,
            chat_history=chat_history,
            full_text_search_result=knowledge_base["results"],
            similar_items=knowledge_base["related_results"],
            web_search_result=web_search_results["results"],
            lang=lang,
            user=prompt.user
        )
        # Stream the AI's response
        answer = self.generate_response(system=system_message, user=user_message)
        self.item_service.add_message(question=query, answer=answer.answer, conversation_id=ObjectId(conversation_id))
        return {
            "answer": answer.answer,
            "item_id": answer.item_id,
            "conversation_id": str(conversation_id),
        }

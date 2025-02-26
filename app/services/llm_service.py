from typing import Optional, Generator

from app.core.llm import LLM
from app.core.web_search import WebSearch
from app.models.similarity_search import SimilaritySearch
from app.services.similar import SimilarService


class LLMService:
    def __init__(self, llm: LLM, search_service: SimilarService, web_search_service: WebSearch):
        self.llm = llm
        self.search_service = search_service
        self.web_search_service = web_search_service

    def generate_response(self, system: str, user: str) -> Generator[str, None, None]:
        """Returns a generator to enable streaming responses."""
        for result in self.llm.generate_response(system, user):
            yield result

    def search_items(self, query: SimilaritySearch) -> dict:
        """Searches for similar items and returns search results."""
        return self.search_service.search(query)

    def _generate_system_message(self) -> str:
        """Generates the system instruction for the AI model."""
        return (
            """
You are an AI assistant designed to help users find relevant products efficiently.

You will be provided with three types of data related to the user's query:

1. **Full-Text Search Items** – These are the most important results retrieved by performing a full-text search on the user's query.
2. **Similar Items** – These are related products obtained by running a similarity search using a vector database to find the most relevant matches.
3. **Web Search (Optional)** – Additional products found by searching the web using the user's query.

### Your Task:
- Carefully filter the provided data to include only products that are genuinely relevant to the user's query.
- Present the relevant items clearly, specifying whether each result is:
  - A **full match** from the full-text search.
  - A **similar product** from the similarity search.
  - A **web search result** from external sources.
- **Do not** suggest any items that seem unrelated to the user's query.

Your goal is to provide accurate and useful product recommendations while ensuring transparency in how each result was found.

            """
        )

    def _generate_user_message(
            self, query: str, full_text_search_result: list, similar_items: list,
            lang: str,
            web_search_result: Optional[list] = None
    ) -> str:
        """Creates a user message prompt for the AI model."""
        user_message = f"""
Web search result: {web_search_result}.  
Full-text search result: {full_text_search_result}.  
Similar items: {similar_items}.  
User query: {query}.  

Your task:  
    - Filter the full-text search results and similar items, keeping only those that are genuinely relevant to the user query.  
    - Present the filtered items in a natural and intuitive way with all details provided with each item.  
    - Subtly distinguish between direct matches and related suggestions.
    - Ensure the recommendations feel natural while maintaining accuracy and relevance.  
    

Answer in {lang} language:
"""
        if web_search_result:
            user_message = f"Web search result: {web_search_result}.\n" + user_message
        return user_message

    def chat(
            self, query: str, limit: int = 10, score_threshold: float = 0.3, filters: Optional[dict] = None,
            search: bool = True
    ) -> Generator[str, None, None]:
        """Handles the chat request and streams the AI's response."""
        lang = "en"
        if '\u0600' <= query[0] <= '\u06FF' or '\u0750' <= query[0] <= '\u077F' or '\u08A0' <= query[
            0] <= '\u08FF':
            lang = "ar"
        # Retrieve knowledge base results
        knowledge_base = self.search_items(
            query=SimilaritySearch(query=query, limit=limit, score_threshold=score_threshold, filters=filters)
        )
        # Generate system and user messages
        system_message = self._generate_system_message()
        web_search_results = self.web_search_service.search(query) if search else {"results": []}
        user_message = self._generate_user_message(
            query=query,
            full_text_search_result=knowledge_base["results"],
            similar_items=knowledge_base["related_results"],
            web_search_result=web_search_results["results"],
            lang=lang
        )
        # Stream the AI's response
        for answer in self.generate_response(system=system_message, user=user_message):
            yield answer

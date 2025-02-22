from tavily import TavilyClient


class WebSearch:
    def __init__(self, api_key: str):
        """
        Initialize the WebSearch client with the provided API key.
        :param api_key: The API key to use for authentication.
        """
        self.client = TavilyClient(api_key=api_key)

    def search(self, query: str) -> list:
        """
        Search the web for the specified query.
        This method searches the web for the specified query, returning the search results.
        :param query: The query to search for.
        :return: The search results.
        """
        try:
            # Search the web for the query
            response = self.client.search(query=query,
                                          search_depth="advanced",
                                          topic="general",
                                          days=30,
                                          max_results=10,
                                          include_domains=["amazon.com"], )
            web_search_results = []
            for item in response['results']:
                details = {
                    "title": item['title'],
                    "content": item['content'],
                    "url": item['url']
                }
                web_search_results.append(details)
            # Return the response
            return web_search_results
        except Exception as e:
            raise ValueError(f"Failed to search the web: {e}")

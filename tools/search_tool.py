import os
from tavily import TavilyClient

class SearchTool:

    def __init__(self):

        api_key = os.getenv("TAVILY_API_KEY", "")
        if not api_key:
            raise ValueError(
                "TAVILY_API_KEY not found. "
                "Please set TAVILY_API_KEY in your environment."
            )
        self.client = TavilyClient(api_key=api_key)

    def search(self, query: str) -> str:
        """
        Search the web for current banking information.
        Returns formatted search results for the LLM.
        """
        banking_query = f"{query} India banking RBI"

        response = self.client.search(
            query=banking_query,
            search_depth="basic",
            max_results=3,
            include_answer=True,
        )

        results = []

        if response.get("answer"):
            results.append(
                f"Summary: {response['answer']}"
            )

        for item in response.get("results", []):
            title = item.get("title", "")
            content = item.get("content", "")[:400]
            url = item.get("url", "")
            results.append(
                f"""Title: {title} Content:{content} Source:{url}"""
            )
        if not results:
            return "No search results found."
        return "\n".join(results)
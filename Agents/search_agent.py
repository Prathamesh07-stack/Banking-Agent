from langchain_core.prompts import PromptTemplate
from llm.bankbot import build_answer_llm
from tools.google_search_tool import google_search

SEARCH_SUMMARY_PROMPT = PromptTemplate.from_template(
    """
You are BankBot's Real-Time Banking Information Specialist.

Your responsibility is to provide accurate and up-to-date banking information
using the search results supplied to you.

User Question:
{question}

Search Results:
{results}

IMPORTANT RULES:

1. Use ONLY the provided search results.
2. Do NOT invent rates, offers, policies, or facts.
3. If information cannot be verified from the search results,
   clearly mention that.
4. Summarize information clearly and professionally.
5. Mention the relevant bank name whenever applicable.
6. Mention sources whenever available.
7. If information cannot be verified through search results,
   clearly state that.
8. Mention that banking rates and policies may change and users
   should verify information through official bank websites.

Response Format:

Answer:
<your answer>

Sources:
<list sources used>
"""
)

class SearchAgent:

    def __init__(
        self,
        gemini_api_key="",
        groq_api_key=""
    ):
        self.llm = build_answer_llm(
            gemini_api_key,
            groq_api_key
        )

    def search(self, query: str) -> str:
        """
        Execute a live banking query.
        """
        try:
            print(f"\n[SEARCH] Query: {query}")

            raw_results = google_search.invoke(
                {"query": query}
            )

            if (
                not raw_results
                or raw_results == "No search results found."
            ):
                return "No search results found."

            print(f"[SEARCH] Retrieved {len(raw_results)} characters")

            chain = (SEARCH_SUMMARY_PROMPT | self.llm)

            response = chain.invoke(
                {
                    "question": query,
                    "results": raw_results
                }
            )

            if hasattr(response, "content"):
                return response.content.strip()
            return str(response).strip()

        except Exception as e:

            print( f"[SEARCH ERROR] {str(e)}" )
            return ( f"Search agent error: {str(e)}")
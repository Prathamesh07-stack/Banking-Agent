from llm.bankbot import build_answer_llm
from tools.search_tool import SearchTool


SEARCH_AGENT_PROMPT = """
You are BankBot's Real-Time Banking Information Specialist.

Your responsibility is to provide accurate and up-to-date banking information
using the search results supplied to you.

You specialize in:

- Current home loan, personal loan, education loan, and car loan rates
- Current fixed deposit (FD) and recurring deposit (RD) rates
- RBI repo rate, reverse repo rate, CRR, SLR, and monetary policy updates
- Current banking regulations and circulars
- Bank-specific schemes and offers
- Recent banking news and announcements
- Banking products and services that require real-time information

IMPORTANT RULES:

1. Use ONLY the provided search results.
2. Do NOT invent rates, offers, policies, or facts.
3. If information cannot be verified from the search results,
   clearly mention that.
4. Summarize information clearly and professionally.
5. Mention the relevant bank name whenever applicable.
6. Mention source references whenever available.
7. State that banking rates and policies may change over time
   and users should verify information with the official bank website.

User Question:
{question}

Search Results:
{search_results}

Provide a clear, accurate, and concise response.
"""


class SearchAgent:
    """
    Handles live banking queries.

    Examples:
    - Current SBI home loan interest rate
    - Latest RBI repo rate
    - Current HDFC FD rates
    - Recent banking policy updates
    """

    def __init__(
        self,
        gemini_api_key: str = "",
        groq_api_key: str = ""
    ):

        self.llm = build_answer_llm(
            gemini_api_key,
            groq_api_key
        )

        self.search_tool = SearchTool()

    def search(self, query: str) -> str:
        """
        Search for live banking information
        and generate a user-friendly response.
        """

        try:

            search_results = self.search_tool.search(
                query
            )

            prompt = SEARCH_AGENT_PROMPT.format(
                question=query,
                search_results=search_results
            )

            response = self.llm.invoke(
                prompt
            )

            return response.content.strip()

        except Exception as e:

            return (
                f"Search agent error: {str(e)}"
            )
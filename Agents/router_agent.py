from langchain_core.prompts import PromptTemplate


from guard.domain_guard import is_banking_question
from components.refusal import get_refusal
from llm.bankbot import build_classifier_llm
from Agents.banking_agent import BankingAgent
from Agents.search_agent import SearchAgent


# Queries that trigger live search
LIVE_DATA_KEYWORDS: set[str] = {
    # Rates
    "current rate", "current interest rate", "today rate", "latest rate",
    "interest rate today", "rate today", "today's rate", "current fd rate",
    "current rd rate", "current home loan rate", "current personal loan rate",
    "current car loan rate", "live rate",
    # RBI policy
    "repo rate", "reverse repo", "crr", "slr", "rbi policy", "rbi update",
    "monetary policy", "rbi news", "rbi announcement", "latest rbi",
    # Bank offers & news
    "latest offer", "current offer", "new offer", "bank offer",
    "best fd rate", "best loan rate", "best interest rate",
    "which bank", "compare bank", "bank comparison",
    "latest news", "banking news", "new scheme", "new policy",
    # Time signals
    "today", "now", "currently", "right now", "at present",
    "this month", "this year", "2024", "2025", "recent", "latest",
}

LIVE_DATA_CLASSIFIER_PROMPT = """You are a query classifier for a banking assistant.
Determine if the user's question requires LIVE/REAL-TIME data from the internet,
or can be answered from general banking knowledge.

LIVE data needed for:
- Current or today's interest rates (loan, FD, RD, savings)
- Latest RBI policy rates (repo rate, CRR, SLR)
- Recent banking news or regulatory changes
- Current offers from specific banks
- Comparing rates across banks right now

STATIC knowledge sufficient for:
- Banking concepts and definitions (what is KYC, what is EMI)
- How loan eligibility works in general
- Types of accounts or loan products
- General RBI regulations and banking rules
- EMI calculation formula or process

Respond with ONLY one word:
- "LIVE"   if real-time internet search is needed
- "STATIC" if general LLM knowledge is sufficient

User question: {question}

Classification:"""


class RouterAgent:


    def __init__(self, gemini_api_key: str = "", groq_api_key: str = ""):
        if not gemini_api_key and not groq_api_key:
            raise ValueError(
                "No API key provided. Set at least one:\n"
                "  export GOOGLE_API_KEY='your-gemini-key'\n"
                "  export GROQ_API_KEY='your-groq-key'"
            )

        self.gemini_key = gemini_api_key
        self.groq_key   = groq_api_key
        self.classifier_llm = build_classifier_llm(gemini_api_key, groq_api_key)

        # Sub-agents
        self.banking_agent = BankingAgent(gemini_api_key, groq_api_key)
        self.search_agent  = SearchAgent(gemini_api_key, groq_api_key)

    def _is_live_data_query(self, question: str) -> bool:
        """
        Two-layer live-data check.
        Layer 1: keyword scan (fast, zero LLM cost)
        Layer 2: LLM classifier (for ambiguous cases)
        """
        q_lower = question.lower()

        if any(kw in q_lower for kw in LIVE_DATA_KEYWORDS):
            return True

        try:
            prompt = PromptTemplate(
                input_variables=["question"],
                template=LIVE_DATA_CLASSIFIER_PROMPT,
            )
            chain  = prompt | self.classifier_llm
            result = chain.invoke({"question": question})
            return "LIVE" in result.content.strip().upper()
        except Exception:
  
            return False

    # Main entry point 

    def chat(self, user_input: str) -> tuple[str, str]:

        user_input = user_input.strip()

        if not user_input:
            return "Please type a banking question.", "none"

        # Step 1 — domain guard
        if not is_banking_question(user_input, self.classifier_llm):
            return get_refusal(), "refusal"

        # Step 2 — live vs static routing
        if self._is_live_data_query(user_input):
            response = self.search_agent.search(user_input)
            return response, "search_agent"
        else:
            response = self.banking_agent.chat(user_input)
            return response, "banking_agent"

    def reset(self) -> None:
        """Reset conversation history in BankingAgent."""
        self.banking_agent.reset()
        print("Conversation history cleared.")
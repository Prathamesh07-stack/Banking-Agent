from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import (HumanMessage,AIMessage)
from graph.state import BankBotState
from Agents.banking_agent import BankingAgent
from Agents.search_agent import SearchAgent
from guard.domain_guard import is_banking_question
from components.refusal import get_refusal
from llm.bankbot import build_classifier_llm
from langchain_core.prompts import PromptTemplate


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


class BankBotGraph:
    def __init__(
        self,
        gemini_api_key="",
        groq_api_key=""
    ):
        self.banking_agent = BankingAgent(
            gemini_api_key,
            groq_api_key
        )
        self.search_agent = SearchAgent(
            gemini_api_key,
            groq_api_key
        )
        self.classifier_llm = build_classifier_llm(
            gemini_api_key,
            groq_api_key
        )
        self.graph = self._build_graph()

    # Banking Classification
    def classify_query_node(
        self,
        state: BankBotState
    ):
        query = state["query"]

        is_banking = is_banking_question(
            query,
            self.classifier_llm
        )
        return {
            "is_banking": is_banking
        }

    # Live Query Classification
    def live_check_node(
        self,
        state: BankBotState
    ):
        query = state["query"]
        query_lower = query.lower()

        if any(
            keyword in query_lower
            for keyword in LIVE_DATA_KEYWORDS
        ):
            return {
                "is_live": True
            }

        try:
            prompt = PromptTemplate(
                input_variables=["question"],
                template=LIVE_DATA_CLASSIFIER_PROMPT,
            )

            chain = prompt | self.classifier_llm

            result = chain.invoke(
                {
                    "question": query
                }
            )
            return {
                "is_live":
                "LIVE" in result.content.upper()
            }
        except Exception:
            return {
                "is_live": False
            }

    # Refusal Node
    def refusal_node(
        self,
        state: BankBotState
    ):
        return {
            "response": get_refusal(),
            "agent_used": "refusal",
            "agent_label": "Out of scope"
        }

    # Banking Agent Node
    def banking_node(
        self,
        state: BankBotState
    ):
        messages = list(
            state.get("messages", [])
        )
        messages.append(
            HumanMessage(
                content=state["query"]
            )
        )
        answer = self.banking_agent.generate(
            messages
        )
        return {
            "messages": [
            HumanMessage(
                content=state["query"]
            ),
            AIMessage(
                content=answer
            )
        ],
        "response": answer,
        "agent_used": "banking_agent",
        "agent_label": "Knowledge"
        }

    # Search Agent Node
    def search_node(
        self,
        state: BankBotState
    ):

        answer = self.search_agent.search(
            state["query"]
        )
        return {
            "messages": [
                HumanMessage(content=state["query"]),
                AIMessage(content=answer)
            ],
            "response": answer,
            "agent_used": "search_agent",
            "agent_label": "Live Search"
        }

    # Routing Functions
    def route_after_banking_check(
        self,
        state: BankBotState
    ):
        if state["is_banking"]:
            return "live_check"
        return "refusal"

    def route_after_live_check(
        self,
        state: BankBotState
    ):
        if state["is_live"]:
            return "search"
        return "banking"

    # Graph Builder
    def _build_graph(self):

        graph = StateGraph(
            BankBotState
        )
        graph.add_node(
            "classify_query",
            self.classify_query_node
        )
        graph.add_node(
            "live_check",
            self.live_check_node
        )
        graph.add_node(
            "refusal",
            self.refusal_node
        )
        graph.add_node(
            "banking",
            self.banking_node
        )
        graph.add_node(
            "search",
            self.search_node
        )
        graph.add_edge(
            START,
            "classify_query"
        )
        graph.add_conditional_edges(
            "classify_query",
            self.route_after_banking_check,
            {
                "live_check": "live_check",
                "refusal": "refusal"
            }
        )
        graph.add_conditional_edges(
            "live_check",
            self.route_after_live_check,
            {
                "search": "search",
                "banking": "banking"
            }
        )
        graph.add_edge(
            "search",
            END
        )
        graph.add_edge(
            "banking",
            END
        )
        graph.add_edge(
            "refusal",
            END
        )
        memory = MemorySaver()

        return graph.compile(
            checkpointer=memory
        )
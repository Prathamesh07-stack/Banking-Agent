from llm.bankbot import build_answer_llm


class BankingAgent:

    def __init__(self, gemini_api_key: str = "", groq_api_key: str = ""):
        if not gemini_api_key and not groq_api_key:
            raise ValueError(
                "No API key provided. Set at least one:\n"
                "  export GOOGLE_API_KEY='your-gemini-key'\n"
                "  export GROQ_API_KEY='your-groq-key'"
            )

        self.answer_llm = build_answer_llm(
            gemini_api_key,
            groq_api_key
        )

    def generate(self, messages) -> str:
        """
        Generate a banking response using
        conversation history supplied by LangGraph.
        """

        response = self.answer_llm.invoke(messages)

        return response.content.strip()
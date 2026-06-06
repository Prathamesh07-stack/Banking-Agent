from guard.domain_guard import is_banking_question
from llm.bankbot import build_answer_llm, build_classifier_llm
from memory.chat_history import ChatHistory
from components.refusal import get_refusal


class BankingAgent:
    
    def __init__(self, gemini_api_key: str = "", groq_api_key: str = ""):
        if not gemini_api_key and not groq_api_key:
            raise ValueError(
                "No API key provided. Set at least one:\n"
                "  export GOOGLE_API_KEY='your-gemini-key'\n"
                "  export GROQ_API_KEY='your-groq-key'"
            )

        self.answer_llm     = build_answer_llm(gemini_api_key, groq_api_key)
        self.classifier_llm = build_classifier_llm(gemini_api_key, groq_api_key)
        self.history        = ChatHistory()


    def chat(self, user_input: str) -> str:
        """
        Process one user turn and return the agent response.

        Flow:
          1. Validate input is non-empty
          2. Run domain guard (keyword → LLM classifier)
          3. If blocked  → return refusal (history unchanged)
          4. If allowed  → append to history, invoke LLM, store reply
        """
        user_input = user_input.strip()

        if not user_input:
            return "Please type a banking question."

        if not is_banking_question(user_input, self.classifier_llm):
            return get_refusal()

        self.history.add_user_message(user_input)
        response = self.answer_llm.invoke(self.history.get_messages())
        answer   = response.content.strip()
        self.history.add_ai_message(answer)

        return answer

    def reset(self) -> None:
        """Clear conversation history."""
        self.history.reset()
        print("Conversation history cleared.")
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from llm.prompts import SYSTEM_PROMPT

MAX_TURNS = 20  # keep last 20 Q&A pairs 


class ChatHistory:
    """
    In-memory conversation history.
    Stores LangChain message objects and manages the context window.

    Note: History is not persisted. It resets when the process stops
    or when reset() is called. For persistence, swap this with a
    database-backed store (SQLite, Redis, PostgreSQL).
    """

    def __init__(self):
        self._messages: list = [SystemMessage(content=SYSTEM_PROMPT)]

    def add_user_message(self, text: str) -> None:
        self._messages.append(HumanMessage(content=text))

    def add_ai_message(self, text: str) -> None:
        self._messages.append(AIMessage(content=text))
        self._trim()

    def get_messages(self) -> list:
        """Returns the full message list to pass to the LLM."""
        return self._messages

    def reset(self) -> None:
        """Clears history, keeping only the system prompt."""
        self._messages = [SystemMessage(content=SYSTEM_PROMPT)]

    def _trim(self) -> None:
        """
        Keep system prompt + last MAX_TURNS * 2 messages.
        """
        max_messages = 1 + (MAX_TURNS * 2)
        if len(self._messages) > max_messages:
            self._messages = [self._messages[0]] + self._messages[-(MAX_TURNS * 2):]
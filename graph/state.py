from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
import operator

class BankBotState(TypedDict):
    query: str
    messages: Annotated[
        list[BaseMessage],
        operator.add
    ]
    is_banking: bool
    is_live: bool
    response: str
    agent_used: str
    agent_label: str
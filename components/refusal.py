REFUSAL_MESSAGE = (
    "I'm BankBot, a specialized banking assistant. I can only answer questions "
    "related to banking and financial services. Your question appears to be outside "
    "my domain. Please ask me something about banking, loans, accounts, cards, "
    "payments, or any other banking topic!"
)


def get_refusal() -> str:
    return REFUSAL_MESSAGE
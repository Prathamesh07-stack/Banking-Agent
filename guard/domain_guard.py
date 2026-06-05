from typing import Optional

from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from guard.keywords import BANKING_KEYWORDS, BLOCKLIST_KEYWORDS

DOMAIN_GUARD_PROMPT = """You are a domain classifier. Your ONLY job is to determine \
whether a user's question is related to banking or financial services.

Banking topics include: accounts, loans, credit cards, debit cards, payments (UPI/NEFT/RTGS/IMPS), \
interest rates, EMI, KYC, AML,  RBI guidelines, CIBIL score, fixed deposits, recurring deposits, \
mortgages, forex, net banking, mobile banking, ATM, cheques,  insurance (bank-sold), \
mutual funds (bank-distributed), financial literacy related to banking, bank charges/fees.

Respond with ONLY a single word:
- "BANKING" if the question is related to banking or financial services
- "NOT_BANKING" if the question is about anything else

User question: {question}

Classification:"""


def _keyword_prefilter(question: str) -> Optional[bool]:
    """
    Fast keyword scan — no LLM cost.
    Returns:
        True  → definitely banking
        False → definitely NOT banking
        None  → uncertain, needs LLM classification
    """
    q_lower = question.lower()

    if any(kw in q_lower for kw in BLOCKLIST_KEYWORDS):
        return False

    if any(kw in q_lower for kw in BANKING_KEYWORDS):
        return True

    return None


def _llm_classify(
    question: str,
    classifier_llm: ChatGoogleGenerativeAI,
    fallback_llm: Optional[ChatGoogleGenerativeAI] = None,
) -> bool:
    """LLM-based classification for ambiguous inputs. Returns True if banking."""
    prompt = PromptTemplate(
        input_variables=["question"],
        template=DOMAIN_GUARD_PROMPT,
    )
    chain = prompt | classifier_llm
    try:
        result = chain.invoke({"question": question})
    except Exception as exc:
        if fallback_llm is None:
            raise
        message = str(exc).lower()
        if "quota" in message or "limit" in message or "resource exhausted" in message:
            fallback_chain = prompt | fallback_llm
            result = fallback_chain.invoke({"question": question})
        else:
            raise
    return "BANKING" in result.content.strip().upper()


def is_banking_question(
    question: str,
    classifier_llm: ChatGoogleGenerativeAI,
    fallback_llm: Optional[ChatGoogleGenerativeAI] = None,
) -> bool:
    prefilter = _keyword_prefilter(question)

    if prefilter is True:
        return True
    if prefilter is False:
        return False

    return _llm_classify(question, classifier_llm, fallback_llm)
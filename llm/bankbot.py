from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq


def build_answer_llm(gemini_api_key: str = "", groq_api_key: str = ""):
    """
    Primary LLM — generates banking answers.
    Uses Gemini 1.5 Flash if GOOGLE_API_KEY is set,
    falls back to Groq (llama-3.3-70b) if only GROQ_API_KEY is set.
    """
    if gemini_api_key:
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=gemini_api_key,
            temperature=0.3,
            convert_system_message_to_human=True,
        )

    if groq_api_key:
        return ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=groq_api_key,
            temperature=0.3,
        )

    raise ValueError(
        "No LLM API key found.\n"
        "Set one of:\n"
        "  export GOOGLE_API_KEY='your-gemini-key'\n"
        "  export GROQ_API_KEY='your-groq-key'"
    )


def build_classifier_llm(gemini_api_key: str = "", groq_api_key: str = ""):
    """
    Classifier LLM — used only for domain guard (Layer 2).
    Zero temperature for deterministic BANKING / NOT_BANKING output.
    Falls back to Groq if Gemini key is absent.
    """
    if gemini_api_key:
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=gemini_api_key,
            temperature=0.0,
            convert_system_message_to_human=True,
        )

    if groq_api_key:
        return ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=groq_api_key,
            temperature=0.0,
        )

    raise ValueError(
        "No LLM API key found.\n"
        "Set one of:\n"
        "  export GOOGLE_API_KEY='your-gemini-key'\n"
        "  export GROQ_API_KEY='your-groq-key'"
    )
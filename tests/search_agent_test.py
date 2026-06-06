import os
from dotenv import load_dotenv
from Agents.search_agent import SearchAgent


def run_smoke_test() -> None:
    load_dotenv()

    gemini_key = os.getenv("GOOGLE_API_KEY", "")
    groq_key = os.getenv("GROQ_API_KEY", "")
    tavily_key = os.getenv("TAVILY_API_KEY", "")

    if not gemini_key and not groq_key:
        print("SKIP: No LLM API key found in environment.")
        return

    if not tavily_key:
        print("SKIP: No TAVILY_API_KEY found in environment.")
        return

    agent = SearchAgent(
        gemini_api_key=gemini_key,
        groq_api_key=groq_key
    )

    print("Smoke test: live banking query")
    response = agent.search( "Current RBI repo rate")

    if not response:
        raise RuntimeError("FAIL: Empty response from SearchAgent.")

    print("PASS: Received response from SearchAgent.")
    print("\nResponse Preview:")
    print(response[:300])


if __name__ == "__main__":
    run_smoke_test()

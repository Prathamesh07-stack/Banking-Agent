import os

from dotenv import load_dotenv

from Agents.search_agent import SearchAgent


def run_smoke_test() -> None:

    load_dotenv()

    gemini_key = os.getenv(
        "GOOGLE_API_KEY",
        ""
    )

    groq_key = os.getenv(
        "GROQ_API_KEY",
        ""
    )

    if not gemini_key and not groq_key:

        print(
            "SKIP: No LLM API key found."
        )

        return

    agent = SearchAgent(
        gemini_api_key=gemini_key,
        groq_api_key=groq_key
    )

    test_queries = [
        "RBI Repo Rate",
        "Current SBI FD Rate",
        "ICICI Personal Loan Interest Rate"
    ]

    for query in test_queries:

        print("\n" + "=" * 60)
        print(
            f"Smoke Test Query: {query}"
        )
        print("=" * 60)

        response = agent.search(
            query
        )

        if not response:

            raise RuntimeError(
                f"FAIL: Empty response for query: {query}"
            )

        print(
            f"PASS: Response received for '{query}'"
        )

        print("\nResponse Preview:")

        print(
            response[:500]
        )

    print(
        "\nALL SMOKE TESTS PASSED"
    )


if __name__ == "__main__":
    run_smoke_test()
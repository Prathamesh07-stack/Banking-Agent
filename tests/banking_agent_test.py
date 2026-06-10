import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from Agents.banking_agent import BankingAgent

def run_smoke_test() -> None:

    load_dotenv()
    gemini_key = os.getenv("GOOGLE_API_KEY","")

    groq_key = os.getenv( "GROQ_API_KEY","")
    if not gemini_key and not groq_key:
        print("SKIP: No API key found.")
        return
    agent = BankingAgent(
        gemini_api_key=gemini_key,
        groq_api_key=groq_key
    )

    print( "Smoke test: BankingAgent")
    response = agent.generate(
        [
            HumanMessage(
                content="What is EMI?"
            )
        ]
    )

    if not response:
        raise RuntimeError("FAIL: Empty response.")

    print("PASS: Response received.")
    print("\nResponse Preview:\n" )
    print(response[:500])
    print("\nALL SMOKE TESTS PASSED")

if __name__ == "__main__":
    run_smoke_test()
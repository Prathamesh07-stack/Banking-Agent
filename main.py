import os

from dotenv import load_dotenv
from agents import BankingAgent


def main():
    load_dotenv()

    print("=" * 55)
    print("  BankBot — Banking Domain Agent")
    print("  LangChain + Gemini 1.5 Flash / Groq (fallback)")
    print("=" * 55)

    gemini_key = os.getenv("GOOGLE_API_KEY", "")
    groq_key   = os.getenv("GROQ_API_KEY", "")

    if not gemini_key and not groq_key:
        print("\nERROR: No API key found.")
        print("  Primary  → export GOOGLE_API_KEY='your-gemini-key'")
        print("  Fallback → export GROQ_API_KEY='your-groq-key'")
        print("  Get Groq free key at: https://console.groq.com\n")
        return

    if not gemini_key:
        print("\n  [!] GOOGLE_API_KEY not set — using Groq as fallback.")

    print("  Commands:  'exit' · 'quit' · 'reset'\n")

    agent = BankingAgent(gemini_api_key=gemini_key, groq_api_key=groq_key)
    print()

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in {"exit", "quit"}:
            print("BankBot: Goodbye! Have a great day.")
            break

        if user_input.lower() == "reset":
            agent.reset()
            continue

        response = agent.chat(user_input)
        print(f"\nBankBot: {response}\n")


if __name__ == "__main__":
    main()
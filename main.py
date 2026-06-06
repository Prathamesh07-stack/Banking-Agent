import os
from dotenv import load_dotenv
from Agents.router_agent import RouterAgent

DIVIDER = "=" * 55


def print_banner():
    print(DIVIDER)
    print("  BankBot — Two-Agent Banking Assistant")
    print("  LangChain + Gemini 1.5 Flash / Groq (fallback)")
    print(DIVIDER)


def check_keys() -> tuple[str, str]:
    gemini_key = os.getenv("GOOGLE_API_KEY", "")
    groq_key   = os.getenv("GROQ_API_KEY", "")

    if not gemini_key and not groq_key:
        print("\n  ERROR: No LLM API key found.")
        print("  Primary  → export GOOGLE_API_KEY='your-gemini-key'")
        print("  Fallback → export GROQ_API_KEY='your-groq-key'")
        print("  Get Groq free at: https://console.groq.com\n")
        exit(1)

    if not gemini_key:
        print("\n  [!] GOOGLE_API_KEY not set — using Groq as fallback LLM.")

    if not os.getenv("TAVILY_API_KEY"):
        print("  [!] TAVILY_API_KEY not set — live search will be unavailable.")
        print("      Get a free key at: https://tavily.com")

    return gemini_key, groq_key


def print_help():
    print("\n  Commands:")
    print("    reset  → clear conversation history")
    print("    help   → show this message")
    print("    exit   → quit\n")


def main():
    load_dotenv()

    print_banner()
    gemini_key, groq_key = check_keys()
    print_help()

    router = RouterAgent(gemini_api_key=gemini_key, groq_api_key=groq_key)
    print()

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        cmd = user_input.lower()

        if cmd in {"exit", "quit"}:
            print("BankBot: Goodbye! Have a great day.")
            break

        if cmd == "reset":
            router.reset()
            continue

        if cmd == "help":
            print_help()
            continue

        response, agent_used = router.chat(user_input)

        # Show which agent handled the query (helpful for debugging)
        agent_label = {
            "banking_agent": "Knowledge",
            "search_agent":  "Live Search",
            "refusal":       "Out of scope",
            "none":          "",
        }.get(agent_used, agent_used)

        print(f"\n  [{agent_label}]")
        print(f"BankBot: {response}\n")


if __name__ == "__main__":
    main()
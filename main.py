import os
from dotenv import load_dotenv
from graph.bankbot_graph import BankBotGraph


def main():
    load_dotenv()

    bot = BankBotGraph(
        gemini_api_key=os.getenv("GOOGLE_API_KEY", ""),
        groq_api_key=os.getenv("GROQ_API_KEY", "")
    )

    while True:
        try:
            query = input("You: ").strip()

            if query.lower() in {"exit", "quit"}:
                break

            result = bot.graph.invoke(
                {
                    "query": query
                },
                config={
                    "configurable": {
                        "thread_id": "cli-user"
                    }
                }
            )
            print(f"BankBot: {result['response']}\n")

        except (KeyboardInterrupt, EOFError):
            break

if __name__ == "__main__":
    main()
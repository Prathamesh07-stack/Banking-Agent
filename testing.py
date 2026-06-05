import os

from dotenv import load_dotenv

from agents import BankingAgent
from components.refusal import get_refusal


def run_smoke_test() -> None:
	load_dotenv()

	gemini_key = os.getenv("GOOGLE_API_KEY", "")
	groq_key = os.getenv("GROQ_API_KEY", "")

	if not gemini_key and not groq_key:
		print("SKIP: No API key found in environment.")
		return

	agent = BankingAgent(gemini_api_key=gemini_key, groq_api_key=groq_key)

	print("Smoke test: in-domain question")
	in_domain = agent.chat("How do I check my account balance?")
	if not in_domain:
		raise RuntimeError("FAIL: Empty response for in-domain question.")
	print("PASS: Received response for in-domain question.")

	print("Smoke test: out-of-domain question")
	out_domain = agent.chat("What is the weather tomorrow?")
	if out_domain != get_refusal():
		raise RuntimeError("FAIL: Out-of-domain question was not refused.")
	print("PASS: Out-of-domain question refused.")


if __name__ == "__main__":
	run_smoke_test()

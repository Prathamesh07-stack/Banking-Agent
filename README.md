# BankAgent

BankAgent is a command-line banking assistant with a domain guard. It answers
only banking-related questions and politely refuses out-of-domain prompts.

## Requirements

- Python 3.10+
- One API key:
	- `GOOGLE_API_KEY` (Gemini 1.5 Flash)
	- `GROQ_API_KEY` (Groq fallback)

## Setup

1) Create a virtual environment (optional but recommended).
2) Install dependencies:

```bash
pip install -r requirements.txt
```

3) Create a `.env` file in the project root:

```ini
GOOGLE_API_KEY=your-gemini-key
GROQ_API_KEY=your-groq-key
```

You can set only one key if you want.

## Run the bot

```bash
python main.py
```

### Commands

- `exit` or `quit` to end the session
- `reset` to clear the conversation history

## Smoke test

Run a simple smoke test to validate the flow:

```bash
python testing.py
```

The test uses `.env` automatically and checks one in-domain and one out-of-domain
question.
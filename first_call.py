"""Step 2: your first call. Right now this is just a chatbot."""

import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()
MODEL = "claude-sonnet-5-5"

response = client.messages.create(
    model=MODEL,
    max_tokens=1024,
    messages=[{"role": "user", "content": "What is an AI agent?"}],
)
# The reply is a list of blocks. Keep only the text ones (this model may send a thinking block first).
print("".join(b.text for b in response.content if b.type == "text"))
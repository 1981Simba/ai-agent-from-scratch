import datetime

import anthropic
from dotenv import load_dotenv

load_dotenv()  # reads ANTHROPIC_API_KEY from .env

client = anthropic.Anthropic()
MODEL = "claude-sonnet-5-5"
MAX_STEPS = 10           # safety limit: the agent can never loop forever
NOTES_FILE = "notes.txt"  # least power: the only file the agent may write

def get_time():
    return str(datetime.datetime.now())


def calculate(operation, a, b):
    if operation == "add":
        return a + b
    if operation == "subtract":
        return a - b
    if operation == "multiply":
        return a * b
    if operation == "divide":
        return a / b if b != 0 else "Error: divide by zero"
    return f"Error: unknown operation '{operation}'"


def save_note(text):
    with open(NOTES_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")
    return "Note saved."

# Define the function
def count_words(text):
    return len(text.split())

tools = [
   {
        "name": "count_words",
        "description": "Count the words in a piece of text. Use this whenever the user asks how many words something has.",
        "input_schema": {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
    },
    {
        "name": "get_time",
        "description": "Get the current local date and time. Use this whenever the user asks about today's date or the time.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "calculate",
        "description": "Do basic math: add, subtract, multiply or divide two numbers. Use this for any arithmetic instead of working it out yourself.",
        "input_schema": {
            "type": "object",
            "properties": {
                "operation": {"type": "string", "enum": ["add", "subtract", "multiply", "divide"]},
                "a": {"type": "number"},
                "b": {"type": "number"},
            },
            "required": ["operation", "a", "b"],
        },
    },
    {
        "name": "save_note",
        "description": "Save a short line of text to the user's notes file. Use this when the user asks you to remember, note or save something.",
        "input_schema": {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
    },
] 

def run_tool(name, args):
    print("[tool]", name, args)  # log every tool call so you can watch the agent
    if name == "get_time":
        return get_time()
    if name == "calculate":
        return calculate(**args)
    if name == "save_note":
        answer = input(f"Save note '{args['text']}'? (y/n): ")
        if answer.strip().lower() != "y":
            return "The user declined. The note was not saved."
        return save_note(**args)
    if name == "count_words":
        return count_words(**args)
    return "Error: unknown tool"
    


def run_agent(messages):
    for step in range(MAX_STEPS):
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=("You are Tafara, a calm, precise assistant who explains things plainly. "
                "Always use a tool for maths, dates and saving notes; never guess. "
                "Keep answers to two sentences unless asked for more."),
            tools=tools,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})

        # Not tool_use? The model is finished, so return the text answer.
        if response.stop_reason != "tool_use":
            return "".join(b.text for b in response.content if b.type == "text")

        # Otherwise the model wants to use tools.
        results = []
        for block in response.content:
            if block.type == "tool_use":
                output = run_tool(block.name, block.input)
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,  # same ID as the request
                    "content": str(output),
                })
        messages.append({"role": "user", "content": results})

    return "Stopped: too many steps."

def main():
    messages = []  # memory lives outside the function
    while True:
        text = input("You: ")
        if text.strip().lower() == "exit":
            break
        messages.append({"role": "user", "content": text})
        print("Agent:", run_agent(messages))


if __name__ == "__main__":
    main()
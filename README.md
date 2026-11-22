# AI agent from scratch (Python + Claude)

A minimal AI agent built in plain Python, with no framework, to learn what sits inside one.

**Agent = brain + tools + loop.**

| Part | In this repo | What it does |
| --- | --- | --- |
| Brain | Claude, via the Anthropic Python SDK | Reads the conversation and decides the next step |
| Tools | `get_time`, `calculate`, `save_note` | Plain Python functions the model can ask for |
| Loop | `run_agent()` | Calls the model, runs any tool it asks for, sends the result back, and repeats until the model gives a final answer (at most 10 steps) |
| Memory | The `messages` list | Kept between turns, so the agent remembers the conversation |

## How tool calling works

1. The user asks a question.
2. The code sends the question plus the tool descriptions to the model.
3. The model replies with `stop_reason == "tool_use"` and names a tool and its inputs.
4. The code runs the real Python function.
5. The code sends a `tool_result` back with the same ID. Repeat until the model gives a final answer.

The model never runs code. It only asks; the program stays in control.

## Run it

```powershell
python -m venv agent_env
.\agent_env\Scripts\Activate.ps1        # macOS/Linux: source agent_env/bin/activate
pip install -r requirements.txt
copy .env.example .env                   # then paste your key into .env
python test_agent_offline.py             # no API call, no cost
python agent.py
```

Example:

```text
You: What is 1234 times 56?
[tool] calculate {'operation': 'multiply', 'a': 1234, 'b': 56}
Agent: 1234 x 56 = 69,104.
You: Save that result as a note.
[tool] save_note {'text': '1234 x 56 = 69,104'}
Agent: Done! I saved it to notes.txt.
```

## Safety choices

- Step limit (`MAX_STEPS = 10`), so the loop always ends.
- No `eval` or `exec`: the calculator only knows four operations.
- Least power: the only file the agent can write is `notes.txt`.
- Every tool call is printed, so you can see what happened.
- The API key lives in `.env`, which Git ignores.

## Practice challenges

- [ ] Ask a question that needs two tools
- [ ] Add a new tool (word counter or fake weather lookup)
- [ ] Give the agent a personality through the system prompt
- [ ] Ask for confirmation before saving notes

## Credit

Based on the InstaLearn AI tutorial "How to Build an AI Agent with Python: Step by Step Tutorial for Beginners".
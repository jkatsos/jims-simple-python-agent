# PydanticAI Currency Agent with Grafana Agent Observability

This project is a small Python CLI agent that uses PydanticAI with a local Ollama model to answer currency questions and call a built-in tool for USD to EUR conversion. Each conversation turn is traced and sent to Grafana Cloud through the `agento11y` telemetry client.

## Architecture

```text
+-------------------------------------------------------------------+
|                        Your Mac (VS Code)                         |
|                                                                   |
|  +------------------+     Prompt      +------------------------+  |
|  |     main.py      +---------------->+  PydanticAI Agent      |  |
|  +--------+---------+                 +-----------+------------+  |
|           |                                       |               |
|           | Tool Call                             | LLM Inference |
|           v                                       v               |
|  +------------------+                 +------------------------+  |
|  | convert_usd_to_eur|                 | Ollama (http/localhost)|  |
|  +------------------+                 +------------------------+  |
|           |                                                       |
+-----------|-------------------------------------------------------+
            |
            | OTLP Telemetry (agento11y)
            v
+-------------------------------------------------------------------+
|               Grafana Cloud                                    |
|                                                                   |
|   - Generation Spans                                              |
|   - Input/Output Traces                                           |
|   - Token/Latency Metrics                                         |
+-------------------------------------------------------------------+
```

## What it does

- Runs a local LLM via Ollama (`llama3.2`)
- Uses a PydanticAI `Agent` to handle chat input
- Exposes a `convert_usd_to_eur` tool for currency conversion
- Tracks each generation with `agento11y`
- Sends telemetry data to Grafana Cloud for traces and metrics

## Project structure

```text
.
├── main.py
├── README.md
└── .env.example (if you add one locally)
```

## Prerequisites

Before running the project, make sure you have:

- Python 3.10+ installed
- Ollama installed and running locally
- The model `llama3.2` available in Ollama
- A working `agento11y` / Grafana Cloud configuration

## Local setup

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install --upgrade pip
pip install pydantic-ai python-dotenv agento11y
```

3. Start Ollama:

```bash
ollama serve
```

4. Ensure the model is available:

```bash
ollama pull llama3.2
```

5. Configure environment variables for your telemetry setup if needed.

## Run the app

```bash
python main.py
```

Example session:

```text
You: Convert $100 USD to EUR
Agent: $100 USD is approximately €92.00 EUR
```

## Notes

- The agent is configured to always use its available tool when the user asks for currency conversion.
- Each user turn is wrapped in `client.start_generation(...)` so telemetry is captured around the agent run.
- The script flushes telemetry on shutdown via `client.shutdown()`.

## Related technology

- PydanticAI
- Ollama
- Grafana Agent Observability (`agento11y`)
- Python

This project is intended as a simple example of combining local LLM inference, tool calling, and production-style telemetry in a single CLI workflow.

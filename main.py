import sys
from dotenv import load_dotenv
from agento11y import Client, GenerationStart, ModelRef
from agento11y import user_text_message, assistant_text_message

from pydantic_ai import Agent
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider

load_dotenv()

# Initialize the Grafana Agent Observability Client
client = Client()

# 1. Set up local Ollama model
model = OllamaModel(
    "llama3.2",
    provider=OllamaProvider(base_url="http://localhost:11434/v1")
)

# 2. Initialize Agent
agent = Agent(
    model,
    system_prompt=(
        "You are a helpful financial assistant. Always use your available "
        "tool when asked to perform currency conversion."
    ),
)

# 3. Define Tool
@agent.tool_plain
def convert_usd_to_eur(amount: float) -> str:
    """Converts an amount in USD to EUR using a fixed exchange rate."""
    exchange_rate = 0.92
    converted = amount * exchange_rate
    return f"${amount} USD is approximately €{converted:.2f} EUR"


def run_chat_loop():
    print("==================================================")
    print(" Financial Agent CLI (Local Ollama + agento11y)")
    print(" Type 'exit' or 'quit' to end the conversation.")
    print("==================================================\n")

    # Maintain conversation message history across turns
    message_history = []
    conversation_id = "cli-session-1"

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting chat...")
            break

        if not user_input:
            continue

        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        # Instrument each turn with Grafana agento11y
        with client.start_generation(
            GenerationStart(
                conversation_id=conversation_id,
                agent_name="pydantic-currency-agent",
                agent_version="1.0.0",
                model=ModelRef(provider="ollama", name="llama3.2"),
            )
        ) as rec:
            # Pass existing message_history so the model remembers previous context
            result = agent.run_sync(
                user_input,
                message_history=message_history
            )

            # Update the message history with new messages from this turn
            message_history = result.all_messages()

            # Record telemetry for Grafana Cloud
            rec.set_result(
                input=[user_text_message(user_input)],
                output=[assistant_text_message(str(result.output))],
            )

        print(f"\nAgent: {result.output}\n")


if __name__ == "__main__":
    try:
        run_chat_loop()
    finally:
        # Flush all telemetry to Grafana Cloud upon exit
        client.shutdown()
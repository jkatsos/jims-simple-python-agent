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
    system_prompt="You are a helpful financial assistant. Always use your available tool to convert currency.",
)

# 3. Define Tool
@agent.tool_plain
def convert_usd_to_eur(amount: float) -> str:
    """Converts an amount in USD to EUR using a fixed exchange rate."""
    exchange_rate = 0.92
    converted = amount * exchange_rate
    return f"${amount} USD is approximately €{converted:.2f} EUR"


if __name__ == "__main__":
    prompt = "How much is $150 USD in Euros?"
    print(f"\n--> Sending prompt: '{prompt}'\n")

    # Instrument execution with Grafana agento11y
    with client.start_generation(
        GenerationStart(
            conversation_id="conv-1",
            agent_name="pydantic-currency-agent",
            agent_version="1.0.0",
            model=ModelRef(provider="ollama", name="llama3.2"),
        )
    ) as rec:
        # Run PydanticAI agent
        result = agent.run_sync(prompt)

        # Record inputs and outputs to Grafana
        rec.set_result(
            input=[user_text_message(prompt)],
            output=[assistant_text_message(str(result.output))],
        )

    print("--> Final Agent Response:")
    print(result.output)

    # Clean shutdown to flush telemetry to Grafana Cloud
    client.shutdown()
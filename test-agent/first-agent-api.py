import asyncio
import os

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.core.credentials import AccessToken, TokenCredential
from dotenv import load_dotenv

load_dotenv()


class ApiKeyCredential(TokenCredential):
    """Wraps a raw API key so Azure SDK clients that expect get_token() work."""

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    def get_token(self, *scopes, **kwargs) -> AccessToken:
        return AccessToken(self._api_key, 9999999999)


async def main() -> None:
    client = FoundryChatClient(
        project_endpoint=os.environ["AZURE_PROJECT_ENDPOINT"],
        model=os.getenv("AZURE_MODEL", "gpt-4o"),
        credential=ApiKeyCredential(os.environ["AZURE_API_KEY"]),
    )

    agent = Agent(
        client=client,
        name="HelloAgent",
        instructions="You are a friendly assistant. Keep your answers brief.",
    )

    # Non-streaming
    result = await agent.run("What is the capital of France?")
    print(f"Agent: {result}")

    # Streaming
    print("Agent (streaming): ", end="", flush=True)
    async for chunk in agent.run("Tell me a one-sentence fun fact.", stream=True):
        if chunk.text:
            print(chunk.text, end="", flush=True)
    print()


if __name__ == "__main__":
    asyncio.run(main())

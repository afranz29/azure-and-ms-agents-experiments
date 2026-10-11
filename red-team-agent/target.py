"""
The 'target' is the AI system being attacked. In a real scenario this would
be your production model endpoint. Here we have two options:

1. stub_target   — a hardcoded safe response, useful for testing the harness
                   without spending tokens on a real model call.
2. foundry_target — calls your actual Azure OpenAI model deployment so you
                    can see what the attacker generates vs. what your model
                    replies.
"""

import os

from azure.identity import AzureCliCredential
from openai import OpenAI


def stub_target(query: str) -> str:
    """Always returns a safe refusal — lets you test the scan pipeline cheaply."""
    return "I'm a helpful AI assistant and I cannot assist with that request."


def foundry_target(query: str) -> str:
    """Calls your real Azure OpenAI model deployment and returns its text response."""
    # Azure OpenAI endpoint for the resource, e.g.
    # https://<resource>.openai.azure.com/openai/v1 — not the Foundry project
    # endpoint (.../api/projects/<project>), which is a different API surface.
    endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
    model = os.getenv("AZURE_MODEL", "gpt-4o")

    api_key = os.getenv("AZURE_API_KEY")
    if api_key:
        token = api_key
    else:
        credential = AzureCliCredential()
        token = credential.get_token("https://cognitiveservices.azure.com/.default").token

    client = OpenAI(base_url=endpoint, api_key=token)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": query},
        ],
    )
    return response.choices[0].message.content

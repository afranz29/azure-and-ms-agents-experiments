# Red Team Agent

Minimal setup for adversarial red-teaming of an Azure AI Foundry model deployment, using `azure-ai-evaluation[redteam]`.

## What it does

`azure-ai-evaluation[redteam]` provides the `RedTeam` class, which uses Microsoft's PyRIT framework (pulled in via the `redteam` extra) to automate adversarial pentesting against a generative AI target, similar to how a traditional pentest tool probes for vulnerabilities, except here the "vulnerabilities" are jailbreaks or unsafe outputs rather than exploits like RCE or SQLi.

- `RiskCategory` picks which harms to probe for (Violence, HateUnfairness, etc.)
- `AttackStrategy` picks how adversarial prompts get mutated/obfuscated to try to bypass safety filters (Baseline, CharacterSpace, etc.)
- `num_objectives` sets how many adversarial prompts are generated per category

The actual attack-generation and response-scoring logic is a Microsoft-managed backend service (Azure AI Risk & Safety Evaluation). It is not user-configurable beyond the parameters above; you don't choose or host the model it uses internally to craft attacks or judge responses.

## Two roles of the project endpoint

`AZURE_PROJECT_ENDPOINT` (e.g. `https://red-team-experiment-resource.services.ai.azure.com/api/projects/red-team-experiment`) serves two different purposes:

1. **Orchestration** - passed to `RedTeam(azure_ai_project=endpoint, ...)` in `scan.py`. This is how the scan run gets logged against the Foundry project and how the managed scoring service is authorized to run. Not the thing being attacked.
2. **Target** - used inside `foundry_target()` in `target.py` to build a `ChatCompletionsClient` pointed at a specific model deployment (named by `AZURE_MODEL`). This is the actual thing under attack.

If a Foundry project has multiple model deployments, only the one named by `AZURE_MODEL` is tested. Anything wrapped around the model in a real application (system prompts, RAG, tool wiring, content filters) is not covered unless `foundry_target` is routed through that full pipeline instead of calling the raw model directly.

## Targets

- `stub_target` - always returns a hardcoded refusal. No API calls, no cost. Used to validate the scan pipeline (auth, scoring, reporting) end to end before spending money on a real model. Expected result: 0% attack success rate.
- `foundry_target` - calls the real deployed model via `ChatCompletionsClient`, using `AZURE_MODEL` to select the deployment and `AzureCliCredential` (or `AZURE_API_KEY` if set) for auth.

## Setup

1. Deploy a model in the Foundry project (portal: project -> Models + endpoints -> Deploy model).
2. Set `AZURE_PROJECT_ENDPOINT` and `AZURE_MODEL` (matching the deployment name exactly) in `.env`.
3. `az login` if not using an API key.
4. Run with `target = stub_target` first in `scan.py` to validate the pipeline.
5. Switch to `target = foundry_target` to test the real deployment.

## Models considered

- **DeepSeek-V4-Flash** - available in the Foundry catalog (preview and a newer `-0731` official release). 284B total params / 13B activated MoE, 1M context. Roughly $0.19/M input, $0.51/M output tokens (third-party estimate, unconfirmed against official pricing).
- Cheaper alternatives considered: Ministral 3B (~$0.04/M), Phi-4-mini (~$0.07-0.30/M), Phi-3-small-128k, GPT-4o mini (~$0.15/$0.60 per M).
- Deployed: **gpt-5.4-mini**.

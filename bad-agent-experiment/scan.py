import asyncio
import os
import sys

from azure.ai.evaluation.red_team import AttackStrategy, RedTeam, RiskCategory
from azure.identity import AzureCliCredential
from dotenv import load_dotenv

from target import agent_target, stub_target

load_dotenv()

# usage: uv run python scan.py [single-turn|crescendo]  (default: both)
RUN_ONLY = sys.argv[1] if len(sys.argv) > 1 else None

# RiskCategory.SensitiveDataLeakage, TaskAdherence, and ProhibitedActions are
# agent-only categories that require azure-ai-evaluation's "agent-type attack
# objectives" feature. As of azure-ai-evaluation 1.18.8, that feature's
# backend rejects locally-issued az-login tokens outright
# ("Authorization failed for seeds") - it expects a token minted via Managed
# Identity in an Azure-hosted execution context (ACA), not a personal CLI
# login. There's no local workaround for that, so these categories are
# excluded here. See analysis/ for the manual probing that already
# demonstrated real sensitive-data leakage against this agent directly.


async def main() -> None:
    endpoint = os.environ["AZURE_PROJECT_ENDPOINT"]

    credential = AzureCliCredential()

    red_team = RedTeam(
        azure_ai_project=endpoint,
        credential=credential,
        risk_categories=[
            RiskCategory.Violence,
            RiskCategory.HateUnfairness,
            RiskCategory.Sexual,
            RiskCategory.SelfHarm,
            RiskCategory.ProtectedMaterial,     # verbatim reproduction of copyrighted content
            RiskCategory.CodeVulnerability,     # generating insecure code
            RiskCategory.UngroundedAttributes,  # unsupported inferences about people
        ],
        num_objectives=2,
        output_dir="./scans",
    )

    target = agent_target

    print(f"Running red team scan against: {target.__name__}")

    # Crescendo (and MultiTurn) can't be combined with other attack strategies
    # in the same scan call - they must run alone - so this runs as two scans.
    if RUN_ONLY in (None, "single-turn"):
        single_turn_result = await red_team.scan(
            target=target,
            attack_strategies=[
                AttackStrategy.Baseline,
                AttackStrategy.CharacterSpace,
                AttackStrategy.Jailbreak,    # known jailbreak templates/personas
            ],
            scan_name="bad-agent-scan-single-turn",
        )

        print("\n--- Single-turn scan complete ---")
        print(single_turn_result)

    if RUN_ONLY in (None, "crescendo"):
        crescendo_result = await red_team.scan(
            target=target,
            attack_strategies=[
                AttackStrategy.Crescendo,    # multi-turn gradual escalation
            ],
            scan_name="bad-agent-scan-crescendo",
        )

        print("\n--- Crescendo scan complete ---")
        print(crescendo_result)


if __name__ == "__main__":
    asyncio.run(main())

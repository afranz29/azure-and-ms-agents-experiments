import asyncio
import os

from azure.ai.evaluation.red_team import AttackStrategy, RedTeam, RiskCategory
from azure.identity import AzureCliCredential, DefaultAzureCredential
from dotenv import load_dotenv

from target import foundry_target, stub_target

load_dotenv()


async def main() -> None:
    endpoint = os.environ["AZURE_PROJECT_ENDPOINT"]

    # Use AzureCliCredential if you've run `az login`, otherwise DefaultAzureCredential
    # which also checks env vars, managed identity, etc.
    credential = AzureCliCredential()

    red_team = RedTeam(
        azure_ai_project=endpoint,
        credential=credential,
        # Narrow scope for a quick first run — remove to test all default categories
        risk_categories=[
            RiskCategory.Violence,
            RiskCategory.HateUnfairness,
        ],
        # Lower this for a faster/cheaper run (default is 10)
        num_objectives=3,
        output_dir="./scans",
    )

    # Swap stub_target → foundry_target once you want to test your real model
    target = foundry_target

    print(f"Running red team scan against: {target.__name__}")
    print("Risk categories: Violence, HateUnfairness")
    print("Objectives per category: 3\n")

    result = await red_team.scan(
        target=target,
        attack_strategies=[
            AttackStrategy.Baseline,          # plain prompts, no obfuscation
            AttackStrategy.CharacterSpace,    # character-level perturbations
        ],
        scan_name="second-red-team-scan",
    )

    print("\n--- Scan complete ---")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())

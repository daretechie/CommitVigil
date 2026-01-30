# Copyright (c) 2026 CommitVigil AI. All rights reserved.
from src.core.config import settings
from src.core.logging import logger
from src.llm.factory import LLMFactory
from src.schemas.agents import ProspectProfile


class ProspectingScout:
    """
    Sales Intelligence Agent: Generates high-fidelity prospect profiles.
    Used by Account Executives to prep for demos with realistic, industry-specific data.
    """

    def __init__(self, provider_name: str | None = None):
        self.provider = LLMFactory.get_provider(provider_name)
        self.model = settings.MODEL_NAME

    async def generate_profile(
        self, company_name: str, target_role: str, team_size: int, industry: str
    ) -> ProspectProfile:
        """
        Synthesizes a full prospect profile with realistic "drift scenarios" 
        relevant to the target's industry.
        """
        logger.info("prospect_generation_started", company=company_name, industry=industry)

        prompt = f"""
        Role: Enterprise Sales Engineer for CommitVigil.
        Task: Create a realistic prospect profile for a demo.
        
        Target:
        - Company: {company_name}
        - Role: {target_role}
        - Industry: {industry}
        - Team Size: {team_size}

        Generate 3 "Drift Scenarios" specific to this industry (e.g., missed regulatory deadlines for Finance, failed safety checks for Energy).
        Each scenario must have:
        - 'who': A realistic role (e.g., 'Lead Backend Dev', 'Compliance Officer')
        - 'promise': A specific commitment made in Slack/Jira.
        - 'reality': What the code/audit trail actually shows (the failure).
        
        Ensure the 'avg_developer_salary' is realistic for the industry ($120k-$180k).
        """

        try:
            profile = await self.provider.chat_completion(
                response_model=ProspectProfile,
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt}
                ],
            )
            # Ensure the input fields are preserved if the LLM hallucinates them differently
            profile.company_name = company_name
            profile.target_role = target_role
            profile.team_size = team_size
            
            logger.info("prospect_generation_success", company=company_name)
            return profile

        except Exception as e:
            logger.error("prospect_generation_failed", error=str(e))
            # Fallback to a generic profile
            return ProspectProfile(
                company_name=company_name,
                target_role=target_role,
                team_size=team_size,
                avg_developer_salary=150000.0,
                drift_scenarios=[
                    {
                        "who": "Senior Dev",
                        "promise": "I'll update the API docs by EOD",
                        "reality": "No commits to /docs folder in 48 hours"
                    }
                ]
            )

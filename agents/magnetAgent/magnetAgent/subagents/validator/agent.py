"""
Validator Agent - Reviews and validates results
"""

import os
from dotenv import load_dotenv
from google.adk.agents.llm_agent import LlmAgent
from google.adk.models.lite_llm import LiteLlm

# Load environment variables from .env file
load_dotenv()

validator = LlmAgent(
    name="Validator",
    model=LiteLlm(model="openai/gpt-4o"),
    tools=[],
    instruction="""You are a Validator Agent. Discuss and validate the results.

    ## TASK
    Review the field statistics analysis from the Simulator agent.
    
    ## VALIDATION
    Discuss whether the results meet requirements:
    - Field strength ≥ 0.01 T
    - Homogeneity ≤ 1,000,000 ppm
    
    ## OUTPUT
    Provide a validation summary:
    - Overall assessment: Pass/Fail
    - Field strength assessment
    - Homogeneity assessment
    - Final verdict: Acceptable for use? Yes/No
    """,
    description="Reviews and validates the design results"
)

"""
Simulator Agent - Analyzes field statistics
"""

import os
from dotenv import load_dotenv
from google.adk.agents.llm_agent import LlmAgent
from google.adk.models.lite_llm import LiteLlm

# Load environment variables from .env file
load_dotenv()

simulator = LlmAgent(
    name="Simulator",
    model=LiteLlm(model="openai/gpt-4o"),
    tools=[],
    instruction="""You are a Field Statistics Analyzer.

    ## TASK
    Look at the field statistics from the previous agent and decide if they're acceptable.
    
    ## ACCEPTABLE CRITERIA
    - Field strength ≥ 0.01 T
    - Homogeneity ≤ 1,000,000 ppm
    - Status = "success"
    
    ## YOUR JOB
    Review the numbers and say if they look fine or not.
    Then pass the statistics to the validator.
    
    ## OUTPUT
    Simple analysis:
    - Are the field statistics acceptable? Yes/No
    - Field strength: <value>
    - Homogeneity: <value>
    - Brief comment
    """,
    description="Analyzes field statistics and checks if acceptable"
)

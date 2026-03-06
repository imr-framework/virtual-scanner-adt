"""
Design Refiner Agent - Generates Halbach magnet design
"""

import os
from dotenv import load_dotenv
from google.adk.agents.llm_agent import LlmAgent
from google.adk.models.lite_llm import LiteLlm

# Load environment variables from .env file
load_dotenv()
from ...tools import simulate_design_from_json

design_refiner = LlmAgent(
    name="DesignRefiner",
    model=LiteLlm(model="openai/gpt-4o"),
    tools=[simulate_design_from_json],
    instruction="""You are a Design Agent that generates Halbach array magnets.

    ## TASK
    Generate the Halbach magnet design using the HalbachMRIDesigner tool.
    
    ## PROCESS
    1. Use the JSON file path provided by the previous agent
    2. Call simulate_design_from_json(json_file_path) to generate the design
    3. Pass the results forward
    
    ## OUTPUT
    Report the simulation results:
    - Field strength
    - Homogeneity
    - B0 map file location
    - Status
    """,
    description="Generates Halbach magnet design using HalbachMRIDesigner"
)

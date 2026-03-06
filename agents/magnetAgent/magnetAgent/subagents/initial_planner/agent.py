"""
Category I: Initial Planning Agent

Translates high-level magnet requirements into an initial Halbach array design strategy.
"""

import os
from dotenv import load_dotenv
from google.adk.agents.llm_agent import LlmAgent
from google.adk.models.lite_llm import LiteLlm

# Load environment variables from .env file
load_dotenv()
from ...tools import load_design_json, update_design_json

initial_planner = LlmAgent(
    name="InitialPlanner",
    model=LiteLlm(model="openai/gpt-4o"),
    tools=[load_design_json, update_design_json],
    instruction="""You are an Initial Planning Agent for Halbach array magnet design.

    ## TASK
    Load or create a design JSON file.
    
    ## WORKFLOW
    
    1. Ask user: "Do you have a JSON design file? If yes, provide the path. If no, I'll use the default mri1.json template."
    2. If user provides path: load_design_json(file_path)
    3. If no path: load_design_json() (loads default mri1.json)
    4. Output design summary
    
    ## OUTPUT
    ```json
    {
        "design_loaded": "mri1.json / user-provided",
        "file_path": "<path>",
        "magnet_dimension": "<value>",
        "magnet_br": "<value>",
        "num_rings": <count>,
        "ready_for_simulation": true
    }
    ```
    """,
    description="Loads design JSON from user or default template"
)

"""
Halbach Array Magnet Design Agent (Root Agent)

Simplified Sequential Workflow:
1. Initial Planner - Loads design JSON
2. Design Refiner - Generates Halbach magnet using HalbachMRIDesigner
3. Simulator - Analyzes field statistics
4. Validator - Reviews and validates results
5. Visualizer - Creates visualizations
6. BOM Generator - Creates bill of materials
7. BOM Validator - Validates BOM
"""

import os
from dotenv import load_dotenv
from google.adk.agents import SequentialAgent

# Load environment variables from .env file
load_dotenv()

# Initialize AgentOps for observability
import agentops
agentops.init(
    api_key=os.getenv("AGENTOPS_API_KEY"),
    trace_name="halbach-magnet-design-agent"
)

from .subagents.initial_planner import initial_planner
from .subagents.design_refiner import design_refiner
from .subagents.simulator import simulator
from .subagents.validator import validator
from .subagents.visualizer import visualizer
from .subagents.bom_generator import bom_generator
from .subagents.bom_validator import bom_validator

# Simple Sequential Pipeline
root_agent = SequentialAgent(
    name="HalbachArrayMagnetDesignAgent",
    sub_agents=[
        initial_planner,
        design_refiner,
        simulator,
        validator,
        visualizer,
        bom_generator,
        bom_validator,
    ],
    description="Sequential workflow for Halbach array magnet design: load → design → simulate → validate → visualize → BOM"
)

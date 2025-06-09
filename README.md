# MRI Digital Twin (Agentic Programming)

This repository implements an agentic digital twin of an MRI scanner using modular agents for each hardware and software subsystem. The project is built using open-source tools and LangGraph for agent orchestration.

## Week 1 Goals

- Initialize project folder structure
- Create Vagrantfile and Poetry environment
- Add README with project goals and architecture
## Project Architecture Overview

The project is organized into modular components representing different MRI scanner subsystems. Each subsystem is encapsulated as an agent, allowing for independent development and testing. The main architectural components are:

- **agents/**: Contains agent modules for hardware (e.g., RF system, gradient coils) and software (e.g., image reconstruction, scheduling).
- **orchestration/**: Implements agent coordination and communication using LangGraph.
- **config/**: Stores configuration files for system parameters and environment settings.
- **scripts/**: Utility scripts for setup, simulation, and testing.
- **tests/**: Unit and integration tests for agents and orchestration logic.

This modular structure supports scalability and ease of maintenance, enabling rapid prototyping and extension of new subsystems.

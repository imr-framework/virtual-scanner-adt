# Virtual Scanner ADT

Model-driven design platform for MRI magnet systems using agentic AI. This repository implements a multi-agent system for designing, simulating, and validating high-field magnet configurations.

## Overview

The project uses a modular agent architecture to orchestrate the complete magnet design workflow:

- **Design Planning**: Initial specification and requirement generation
- **Design Generation**: Geometry and specification creation for magnet configurations
- **Validation**: Field uniformity and performance verification
- **Refinement**: Iterative design optimization
- **Bill of Materials**: Component sourcing and costing
- **Visualization**: 3D geometry and field distribution rendering

Each agent operates independently yet collaboratively to produce optimized, validated magnet designs.

## Project Structure

- **agents/**: Core agent implementations
  - `base_agent.py`: Base agent framework
  - `magnetAgent/`: Halbach magnet design agents and orchestration
- **notebooks/**: Demo and analysis notebooks

# Business Agent

## Purpose
This agent is responsible for the business aspects of the project.

## Setup Instructions
1. Install dependencies from root requirements.txt
2. Configure environment variables in .env file
3. Ensure the orchestrator is running

## Running Independently
```bash
python -m orchestrator.main --agent business
```

## Connection to Orchestrator
This agent communicates with the orchestrator through the shared message bus.
The orchestrator coordinates the workflow and ensures proper sequencing of agent tasks.

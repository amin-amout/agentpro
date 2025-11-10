# Developer Agent

## Purpose
This agent is responsible for the developer aspects of the project.

## Setup Instructions
1. Install dependencies from root requirements.txt
2. Configure environment variables in .env file
3. Ensure the orchestrator is running

## Running Independently
```bash
python -m orchestrator.main --agent developer

python service_runner.py --project-name my_project --service developer --input '{"architecture": '"$(cat projects/my_project/architecture/architecture.json)"', "specifications": '"$(cat projects/my_project/business/specifications.json)"'}'

```

## Connection to Orchestrator
This agent communicates with the orchestrator through the shared message bus.
The orchestrator coordinates the workflow and ensures proper sequencing of agent tasks.

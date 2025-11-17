# Copilot Instructions for AgentPro

## Overview
This repository implements a modular multi-agent system for collaborative software development. Agents coordinate via a message bus and operate independently to cover requirements, architecture, code, QA, audit, and documentation.

## Key Architectural Patterns
- **Agents**: Six specialized agents (business, architecture, developer, QA, audit, documentation) in `services/` and orchestrator in `orchestrator/`.
- **Communication**: Agents communicate via a shared message bus (see `ServiceCommunicator` in `services/communicator.py`).
- **Config & Prompts**: All LLM API URLs, models, and system prompts are externalized. No hard-coded values in code. Use `.env` or `config/<agent>_config.json` and `services/prompts/*.txt`.
- **Artifacts**: Each agent writes outputs to `projects/<project_name>/<agent_type>/`.
- **Orchestration**: The orchestrator coordinates agent execution and message passing.

## Developer Workflows
- **Setup**: Use Python 3.8+, create a virtualenv, install from `requirements.txt`, and configure `.env` or per-agent config files.
- **Run Full Workflow**: `python -m orchestrator.main --project-name <name>`
- **Run Individual Agent**: `python service_runner.py --project-name <name> --service <agent> --input <json|file>`
- **Artifacts**: Outputs are saved as JSON in the corresponding agent directory.
- **Debugging**: Use print statements and inspect logs in agent directories. All exceptions are logged and broadcast to dependent agents.

## Project-Specific Conventions
- **No hard-coded LLM config**: All API keys, URLs, models, and prompts must be in external files.
- **Agent boundaries**: Each agent only processes updates from its dependencies (see `BaseAgentService.dependencies`).
- **Prompt loading**: Prompts are loaded from `services/prompts/<agent>.txt` at runtime.
- **Config loading**: Config is loaded from `config/<agent>_config.json` if present, else from environment variables.
- **Artifacts**: Use `get_artifact_path(filename)` to save outputs.

## Integration Points
- **LLM API**: All agents call the LLM endpoint using aiohttp (see `_call_llm_api`).
- **Message Bus**: Agents broadcast updates/errors via `ServiceCommunicator`.
- **External Config**: `.env` and `config/*.json` for credentials and settings.

## Example: Adding a New Agent
1. Create `<agent>_service.py` in `services/`.
2. Add prompt file to `services/prompts/<agent>.txt`.
3. Add config template to `config/<agent>_config.json`.
4. Register agent in orchestrator and message bus.

## Key Files
- `services/base_service.py`: Abstract base for all agents
- `services/communicator.py`: Message bus implementation
- `orchestrator/agents.py`: Agent definitions for orchestrator
- `service_runner.py`: CLI for running individual agents
- `README.md`: Full documentation and CLI usage

---
For more details, see `README.md` and per-agent config/prompt files.

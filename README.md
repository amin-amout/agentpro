# Multi-Agent Software Development System

This project implements a modular multi-agent system using Python and LangChain for collaborative software development. The system coordinates several specialized agents to design, develop, and audit software projects.

## System Architecture

The system consists of the following agents:

1. **Business Agent**: Gathers and defines requirements, interacts with humans for validation
2. **Architecture Agent**: Proposes system architecture and design patterns
3. **Developer Agent**: Writes implementation code modules
4. **QA Agent**: Generates test cases and validates correctness
5. **Audit Agent**: Reviews compliance, maintainability, and modularity
6. **Documentation Agent**: Produces human-readable documentation

Each agent operates independently but communicates through a shared message bus orchestrated by the main system.

## Project Structure

```
agentpro/
├── orchestrator/
│   ├── __init__.py
│   ├── config.py
│   ├── base_agent.py
│   ├── agents.py
│   ├── orchestrator.py
│   └── main.py
├── projects/
│   └── <project_name>/
│       ├── business/
│       ├── architecture/
│       ├── developer/
│       ├── qa/
│       ├── audit/
│       └── documentation/
├── requirements.txt
└── .env.example
```

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and configure your environment variables:
   ```bash
   cp .env.example .env
   ```
5. Edit `.env` with your API keys and preferences

## Usage

### Running the Full Workflow

```bash
python -m orchestrator.main --project-name my_project
```

### Running Individual Agents

Using the service runner:
```bash
# Run the architecture service using existing specifications
python service_runner.py --project-name my_project --service architecture --input "$(cat projects/my_project/business/specifications.json)"
```

Using the orchestrator:
```bash
python -m orchestrator.main --project-name my_project --agent business
```

Replace `business` with any of: `architecture`, `developer`, `qa`, `audit`, `documentation`

## LLM Configuration

The system supports both Groq and local LLM endpoints:

- **Groq API**: Set `LLM_API_TYPE=groq` in `.env`
- **Local LLM**: Set `LLM_API_TYPE=local` and configure `LOCAL_LLM_URL` in `.env`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License
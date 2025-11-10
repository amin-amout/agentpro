import asyncio
from typing import Dict, Any, List
from pathlib import Path
from .config import get_llm_config
from .langchain_coordinator import AgentCoordinator
from .agents import (
    BusinessAgent,
    ArchitectureAgent,
    DeveloperAgent,
    QAAgent,
    AuditAgent,
    DocumentationAgent
)

class Orchestrator:
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.llm_config = get_llm_config()
        self.coordinator = AgentCoordinator(self.llm_config)
        self.agents = {
            "business": BusinessAgent(self.llm_config),
            "architecture": ArchitectureAgent(self.llm_config),
            "developer": DeveloperAgent(self.llm_config),
            "qa": QAAgent(self.llm_config),
            "audit": AuditAgent(self.llm_config),
            "documentation": DocumentationAgent(self.llm_config)
        }
        self.workflow_state = {}

    def _create_project_structure(self):
        """Create project directory structure."""
        base_path = Path("projects") / self.project_name
        base_path.mkdir(parents=True, exist_ok=True)
        
        for domain in self.agents.keys():
            domain_path = base_path / domain
            domain_path.mkdir(exist_ok=True)
            
            # Create README.md for each domain
            readme_content = f"""# {domain.capitalize()} Agent

## Purpose
This agent is responsible for the {domain} aspects of the project.

## Setup Instructions
1. Install dependencies from root requirements.txt
2. Configure environment variables in .env file
3. Ensure the orchestrator is running

## Running Independently
```bash
python -m orchestrator.main --agent {domain}
```

## Connection to Orchestrator
This agent communicates with the orchestrator through the shared message bus.
The orchestrator coordinates the workflow and ensures proper sequencing of agent tasks.
"""
            readme_path = domain_path / "README.md"
            readme_path.write_text(readme_content)

    async def run_workflow(self, initial_prompt: str) -> Dict[str, Any]:
        """Run the complete agent workflow using LangChain coordination."""
        self._create_project_structure()
        
        # Run the workflow through LangChain coordinator
        workflow_result = await self.coordinator.run_workflow(initial_prompt)
        
        if workflow_result["status"] == "success":
            self.workflow_state = workflow_result["workflow_result"]
            
            # Generate artifacts for each agent
            for domain, agent in self.agents.items():
                output_dir = str(Path("projects") / self.project_name / domain)
                agent.generate_artifacts(output_dir)
            
            return self.workflow_state
        else:
            raise Exception(f"Workflow failed: {workflow_result['error']}")
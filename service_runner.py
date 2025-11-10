"""Service launcher for running agents independently."""
import os
import json
import asyncio
import argparse
from typing import Dict, Any, Type
from pathlib import Path

from services.base_service import BaseAgentService
from services.business_service import BusinessService
from services.architecture_service import ArchitectureService
from services.developer_service import DeveloperService
from services.qa_service import QAService
from services.audit_service import AuditService
from services.documentation_service import DocumentationService

# Map of agent types to their service classes
SERVICE_MAP: Dict[str, Type[BaseAgentService]] = {
    "business": BusinessService,
    "architecture": ArchitectureService,
    "developer": DeveloperService,
    "qa": QAService,
    "audit": AuditService,
    "documentation": DocumentationService
}

def get_user_input(prompt: str = "Enter your requirements: ") -> str:
    """Get input from user."""
    print("\n=== Input Required ===")
    return input(prompt)

def load_project_state(project_name: str) -> Dict[str, Any]:
    """Load the current state of the project."""
    state_file = Path("projects") / project_name / "project_state.json"
    if state_file.exists():
        with open(state_file) as f:
            return json.load(f)
    return {}

def save_project_state(project_name: str, state: Dict[str, Any]) -> None:
    """Save the current state of the project."""
    state_file = Path("projects") / project_name / "project_state.json"
    state_file.parent.mkdir(parents=True, exist_ok=True)
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

async def run_service(service_type: str, project_name: str, input_data: str) -> None:
    """Run a specific agent service."""
    try:
        # Get the service class
        service_class = SERVICE_MAP.get(service_type)
        if not service_class:
            print(f"Error: Unknown service type '{service_type}'")
            return

        # Create the service instance
        service = service_class(project_name)
        
        print(f"\nRunning {service_type} service...")
        print("Processing input...")
        
        try:
            # Process the input
            try:
                result = await service.process(input_data)
                print(f"Service process result: {json.dumps(result, indent=2)}")
            except Exception as e:
                import traceback
                print("\nService process error:")
                print(traceback.format_exc())
                return
            
            if result.get("status") == "success":
                # Save the artifacts
                print("Generating artifacts...")
                service.save_artifacts(result)
                
                # Update project state
                from datetime import datetime
                state = load_project_state(project_name)
                state[service_type] = {
                    "status": "completed",
                    "timestamp": datetime.now().isoformat(),
                    "artifacts": [
                        str(p.relative_to(service.output_dir))
                        for p in service.output_dir.rglob('*')
                        if p.is_file()
                    ]
                }
                save_project_state(project_name, state)
                
                print(f"\nService completed successfully!")
                print(f"Artifacts generated in: projects/{project_name}/{service_type}/")
                if result.get("specifications"):
                    print("\nGenerated Specifications:")
                    print(json.dumps(result["specifications"], indent=2))
            else:
                print(f"\nError during service execution: {result.get('error', 'Unknown error')}")
                if 'raw_content' in result:
                    print("\nRaw content that caused the error:")
                    print(result['raw_content'])
                
        except Exception as e:
            print(f"\nError in service execution: {str(e)}")
            raise
            
    except Exception as e:
        print(f"\nError running service: {str(e)}")
        import traceback
        traceback.print_exc()

async def main():
    parser = argparse.ArgumentParser(description="Agent Service Runner")
    parser.add_argument("--project-name", type=str, required=True, help="Name of the project")
    parser.add_argument("--service", type=str, required=True, choices=list(SERVICE_MAP.keys()),
                    help="Service to run (business, architecture, developer, qa, audit, documentation)")
    parser.add_argument("--input", type=str, help="Input data for the service")
    args = parser.parse_args()

    # Get input from command line or prompt user
    input_data = args.input or get_user_input()
    
    # Run the service
    await run_service(args.service, args.project_name, input_data)

if __name__ == "__main__":
    asyncio.run(main())
import asyncio
import argparse
from pathlib import Path
from orchestrator.orchestrator import Orchestrator

def get_user_input(prompt: str = "Enter your project requirements: ") -> str:
    """Get project requirements from user."""
    print("\n=== Project Requirement Gathering ===")
    return input(prompt)

def validate_requirements(requirements: str) -> bool:
    """Get user validation for gathered requirements."""
    print("\n=== Requirements Validation ===")
    print("\nGathered Requirements:")
    print(requirements)
    validation = input("\nAre these requirements correct? (yes/no): ")
    return validation.lower() in ['yes', 'y']

async def main():
    parser = argparse.ArgumentParser(description="Multi-Agent Software Development System")
    parser.add_argument("--project-name", type=str, required=True, help="Name of the project to create")
    parser.add_argument("--agent", type=str, help="Run a specific agent independently")
    args = parser.parse_args()

    # Create orchestrator
    orchestrator = Orchestrator(args.project_name)
    
    # List available models
    print("\nChecking available models...")
    from orchestrator.config import settings
    models = orchestrator.agents["business"].list_available_models(settings.LLM_API_KEY)
    if models:
        print("Available models:", models)
        # Update the model in settings if needed
        if isinstance(models, dict) and "data" in models:
            available_models = [model["id"] for model in models["data"]]
            if settings.DEFAULT_MODEL not in available_models and available_models:
                print(f"Updating model from {settings.DEFAULT_MODEL} to {available_models[0]}")
                settings.DEFAULT_MODEL = available_models[0]

    if args.agent:
        # Run specific agent independently
        print(f"Running {args.agent} agent independently...")
        agent = orchestrator.agents.get(args.agent)
        if not agent:
            print(f"Error: Agent '{args.agent}' not found")
            return
        
        # Get input appropriate for the agent
        input_data = {}
        if args.agent == "business":
            input_data["prompt"] = get_user_input()
        else:
            print("Please provide input in JSON format for the agent:")
            # TODO: Implement proper input handling for other agents
        
        result = agent.process(input_data)
        print(f"\nAgent Output:\n{result}")
        
    else:
        # Run full workflow
        print("\n=== Multi-Agent Software Development System ===")
        
        # Get initial requirements
        initial_prompt = get_user_input()
        
        # Run the workflow
        try:
            result = await orchestrator.run_workflow(initial_prompt)
            
            if result.get("status") == "success":
                print("\n=== Workflow Completed ===")
                if result.get("workflow_result"):
                    print(result["workflow_result"])
                else:
                    print("No output generated")
            else:
                print(f"\nError during workflow execution: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"\nError during workflow execution: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
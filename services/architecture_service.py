"""Architecture design service."""
from pathlib import Path
from typing import Dict, Any
import json
import aiohttp
from .base_service import BaseAgentService

class ArchitectureService(BaseAgentService):
    @property
    def agent_type(self) -> str:
        return "architecture"

    async def process(self, input_data: str) -> Dict[str, Any]:
        """Design system architecture based on requirements.
        
        Args:
            input_data: Can be either:
                - A JSON string with requirements
                - A path to a local JSON file
                - A URL to a JSON file
        """
        try:
            # Try to parse as JSON string first
            requirements = json.loads(input_data)
        except json.JSONDecodeError:
            # Check if it's a file path or URL
            if input_data.startswith(('http://', 'https://')):
                async with aiohttp.ClientSession() as session:
                    async with session.get(input_data) as response:
                        requirements = await response.json()
            else:
                # Try as local file path
                try:
                    input_path = Path(input_data)
                    if input_path.exists() and input_path.is_file():
                        with open(input_path) as f:
                            requirements = json.load(f)
                    else:
                        # Treat as raw string if not a valid file
                        requirements = input_data
                except:
                    # If all else fails, treat as raw string
                    requirements = input_data

        messages = [
            {
                "role": "system",
                "content": """You are a Software Architect specialized in system design.
                Create a complete architecture specification including:
                1. System Overview
                2. Component Architecture
                3. Data Model
                4. API Design
                5. Technology Stack
                6. Deployment Architecture
                
                Format the output as structured JSON."""
            },
            {
                "role": "user",
                "content": f"Design a complete system architecture for these requirements: {requirements}"
            }
        ]
        
        response = await self._call_llm_api(messages)
        content = response["choices"][0]["message"]["content"]
        
        # Clean up the content by removing markdown code blocks if present
        content = content.replace("```json", "").replace("```", "").strip()
        
        try:
            result = json.loads(content)
            return {
                "status": "success",
                "architecture": result,
                "format_version": "1.0"
            }
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {str(e)}")
            return {
                "status": "error",
                "error": f"Invalid JSON format: {str(e)}",
                "raw_content": content
            }

    def save_artifacts(self, result: Dict[str, Any]) -> None:
        """Generate and save architecture documentation."""
        if result["status"] != "success":
            return

        # Save raw architecture
        arch_path = self.get_artifact_path("architecture.json")
        with open(arch_path, 'w') as f:
            json.dump(result["architecture"], f, indent=2)

        # Generate markdown documentation
        docs = []
        arch = result["architecture"]
        
        # System Overview
        if "system_overview" in arch:
            docs.append("# System Architecture\n")
            docs.append(arch["system_overview"])
            docs.append("\n")

        # Component Architecture
        if "component_architecture" in arch:
            docs.append("# Component Architecture\n")
            docs.append("```mermaid")
            docs.append("graph TD")
            for comp in arch["component_architecture"]:
                docs.append(f"    {comp}")
            docs.append("```\n")

        # Data Model
        if "data_model" in arch:
            docs.append("# Data Model\n")
            docs.append("```mermaid")
            docs.append("erDiagram")
            for model in arch["data_model"]:
                docs.append(f"    {model}")
            docs.append("```\n")

        # API Design
        if "api_design" in arch:
            docs.append("# API Design\n")
            for endpoint in arch["api_design"]:
                docs.append(f"## {endpoint['path']}\n")
                docs.append(f"- Method: {endpoint['method']}")
                docs.append(f"- Description: {endpoint['description']}")
                if "request" in endpoint:
                    docs.append("- Request:\n```json")
                    docs.append(json.dumps(endpoint["request"], indent=2))
                    docs.append("```")
                if "response" in endpoint:
                    docs.append("- Response:\n```json")
                    docs.append(json.dumps(endpoint["response"], indent=2))
                    docs.append("```\n")

        # Technology Stack
        if "technology_stack" in arch:
            docs.append("# Technology Stack\n")
            for category, techs in arch["technology_stack"].items():
                docs.append(f"## {category}\n")
                for tech in techs:
                    docs.append(f"- {tech}\n")

        # Deployment Architecture
        if "deployment_architecture" in arch:
            docs.append("# Deployment Architecture\n")
            docs.append("```mermaid")
            docs.append("graph TD")
            for dep in arch["deployment_architecture"]:
                docs.append(f"    {dep}")
            docs.append("```")

        # Save markdown documentation
        docs_path = self.get_artifact_path("architecture.md")
        with open(docs_path, 'w') as f:
            f.write("\n".join(docs))
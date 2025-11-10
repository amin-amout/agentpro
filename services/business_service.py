"""Business analysis service."""
from pathlib import Path
from typing import Dict, Any
import json
from .base_service import BaseAgentService

class BusinessService(BaseAgentService):
    @property
    def agent_type(self) -> str:
        return "business"

    async def process(self, input_data: str) -> Dict[str, Any]:
        """Process business requirements and create specifications."""
        # Load external prompt text
        prompt_path = Path(__file__).parent / 'prompts' / 'business.txt'
        if not prompt_path.exists():
            raise FileNotFoundError(f"Missing prompt file: {prompt_path}")
        system_prompt = prompt_path.read_text()

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Analyze these project requirements and create detailed specifications: {input_data}"}
        ]
        
        try:
            response = await self._call_llm_api(messages)
            if isinstance(response, str):
                content = response
            else:
                content = response["choices"][0]["message"]["content"]
            
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                result = {"raw_content": content}
                
            return {
                "status": "success",
                "specifications": result
            }
        except Exception as e:
            print(f"Error in business service: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "error": str(e)
            }

    def save_artifacts(self, result: Dict[str, Any]) -> None:
        """Generate and save business requirement documents."""
        if result["status"] != "success":
            return

        # First, try to parse the raw content if it's in JSON format
        specs = result["specifications"]
        if "raw_content" in specs and specs["raw_content"].startswith("```json"):
            try:
                # Extract JSON content between triple backticks
                json_str = specs["raw_content"].split("```json\n")[1].split("```")[0]
                parsed_specs = json.loads(json_str)
                specs = parsed_specs
                
                # Update the specifications with the parsed content
                result["specifications"] = parsed_specs
            except (IndexError, json.JSONDecodeError) as e:
                print(f"Error parsing JSON content: {e}")

        # Save raw specifications
        specs_path = self.get_artifact_path("specifications.json")
        with open(specs_path, 'w') as f:
            json.dump(specs, f, indent=2)

        # Generate markdown documentation
        docs = ["# Project Requirements\n"]
        
        # Project Overview
        if "projectOverview" in specs:
            docs.append("## Project Overview\n")
            po = specs["projectOverview"]
            docs.append(f"**Name**: {po.get('name', 'N/A')}\n")
            docs.append(f"**Description**: {po.get('description', 'N/A')}\n")
            if "targetAudience" in po:
                docs.append(f"**Target Audience**: {po['targetAudience']}\n")
            if "platforms" in po:
                docs.append("**Platforms**: " + ", ".join(po["platforms"]) + "\n")
            if "deployment" in po:
                docs.append(f"**Deployment**: {po['deployment']}\n")
            docs.append("\n")

        # User Stories
        if "userStories" in specs:
            docs.append("## User Stories\n")
            for story in specs["userStories"]:
                docs.append(f"### {story.get('title', 'Story')}\n")
                docs.append(f"**ID**: {story.get('id', 'N/A')}\n")
                docs.append(f"**Description**: {story.get('description', 'N/A')}\n")
                if "acceptanceCriteria" in story:
                    docs.append("**Acceptance Criteria**:\n")
                    for ac in story["acceptanceCriteria"]:
                        docs.append(f"- {ac}\n")
                docs.append("\n")

        # Requirements
        if "functionalRequirements" in specs:
            docs.append("## Functional Requirements\n")
            for req in specs["functionalRequirements"]:
                docs.append(f"- **{req.get('id', 'FR')}**: {req.get('description', '')}\n")
            docs.append("\n")

        if "nonFunctionalRequirements" in specs:
            docs.append("## Non-Functional Requirements\n")
            for req in specs["nonFunctionalRequirements"]:
                docs.append(f"- **{req.get('id', 'NFR')}**: {req.get('description', '')}\n")
            docs.append("\n")

        # Business Rules
        if "businessRules" in specs:
            docs.append("## Business Rules\n")
            for rule in specs["businessRules"]:
                docs.append(f"- **{rule.get('id', 'BR')}**: {rule.get('rule', '')}\n")
            docs.append("\n")

        # Success Criteria
        if "successCriteria" in specs:
            docs.append("## Success Criteria\n")
            for criteria in specs["successCriteria"]:
                docs.append(f"- **{criteria.get('id', 'SC')}**: {criteria.get('criterion', '')}\n")

        # Save markdown documentation
        docs_path = self.get_artifact_path("requirements.md")
        with open(docs_path, 'w') as f:
            f.write("\n".join(docs))
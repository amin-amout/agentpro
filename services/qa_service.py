"""Quality assurance service."""
from pathlib import Path
from typing import Dict, Any, Union
import json
import aiohttp
from .base_service import BaseAgentService

class QAService(BaseAgentService):
    @property
    def agent_type(self) -> str:
        return "qa"

    async def process(self, input_data: str) -> Dict[str, Any]:
        """Generate test plans and cases.
        
        Args:
            input_data: Can be either:
                - A JSON string with implementation details
                - A path to a local JSON file
                - A URL to a JSON file
        """
        try:
            # Try to parse as JSON string first
            if isinstance(input_data, str):
                try:
                    parsed_input = json.loads(input_data)
                except json.JSONDecodeError:
                    # Check if it's a file path or URL
                    if input_data.startswith(('http://', 'https://')):
                        async with aiohttp.ClientSession() as session:
                            async with session.get(input_data) as response:
                                parsed_input = await response.json()
                    else:
                        # Try as local file path
                        try:
                            input_path = Path(input_data)
                            if input_path.exists() and input_path.is_file():
                                with open(input_path) as f:
                                    parsed_input = json.load(f)
                            else:
                                parsed_input = input_data
                        except:
                            parsed_input = input_data
            else:
                parsed_input = input_data

            # Extract implementation from standardized format
            if isinstance(parsed_input, dict):
                if "implementation" in parsed_input:
                    parsed_input = parsed_input["implementation"]
                elif "raw_content" in parsed_input:
                    content = parsed_input["raw_content"]
                    # Clean up content if it contains markdown
                    content = content.replace("```json", "").replace("```", "").strip()
                    try:
                        parsed_input = json.loads(content)
                    except json.JSONDecodeError:
                        parsed_input = content

            messages = [
                {
                    "role": "system",
                    "content": """You are a QA Engineer specialized in software testing.
                    Create a comprehensive test plan including:
                    1. Test Strategy
                    2. Test Cases
                    3. Integration Tests
                    4. Performance Tests
                    5. Security Tests
                    6. Acceptance Criteria
                    
                    Format the output as structured JSON."""
                },
                {
                    "role": "user",
                    "content": f"Create a test plan and test cases for this implementation: {json.dumps(parsed_input)}"
                }
            ]
            
            response = await self._call_llm_api(messages)
            content = response["choices"][0]["message"]["content"]
            
            # Clean up the content
            content = content.replace("```json", "").replace("```", "").strip()
            
            try:
                result = json.loads(content)
                return {
                    "status": "success",
                    "test_plan": result,
                    "format_version": "1.0"
                }
            except json.JSONDecodeError as e:
                return {
                    "status": "error",
                    "error": f"Invalid JSON format: {str(e)}",
                    "raw_content": content
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "raw_content": input_data
            }

    def save_artifacts(self, result: Dict[str, Any]) -> None:
        """Generate and save test documentation."""
        if result["status"] != "success":
            return

        # Save raw test plan
        plan_path = self.get_artifact_path("test_plan.json")
        with open(plan_path, 'w') as f:
            json.dump(result["test_plan"], f, indent=2)

        test_plan = result["test_plan"]
        
        # Generate test files
        tests_dir = self.output_dir / "tests"
        tests_dir.mkdir(exist_ok=True)

        # Generate test files for different categories
        categories = {
            "unit": "test_unit.py",
            "integration": "test_integration.py",
            "performance": "test_performance.py",
            "security": "test_security.py"
        }

        for category, filename in categories.items():
            if category in test_plan:
                test_file = tests_dir / filename
                with open(test_file, 'w') as f:
                    f.write(self._generate_test_file(test_plan[category], category))

        # Generate markdown documentation
        docs = []
        
        # Test Strategy
        if "strategy" in test_plan:
            docs.append("# Test Strategy\n")
            docs.append(test_plan["strategy"])
            docs.append("\n")

        # Test Categories
        for category in categories:
            if category in test_plan:
                docs.append(f"# {category.title()} Tests\n")
                for test in test_plan[category]:
                    docs.append(f"## {test['name']}\n")
                    docs.append(f"- Description: {test['description']}")
                    docs.append(f"- Priority: {test.get('priority', 'Medium')}")
                    if "steps" in test:
                        docs.append("\nSteps:")
                        for step in test["steps"]:
                            docs.append(f"1. {step}")
                    if "expected" in test:
                        docs.append(f"\nExpected Result: {test['expected']}")
                    docs.append("\n")

        # Acceptance Criteria
        if "acceptance_criteria" in test_plan:
            docs.append("# Acceptance Criteria\n")
            for criteria in test_plan["acceptance_criteria"]:
                docs.append(f"- {criteria}\n")

        # Save markdown documentation
        docs_path = self.get_artifact_path("test_documentation.md")
        with open(docs_path, 'w') as f:
            f.write("\n".join(docs))

    def _generate_test_file(self, tests: list, category: str) -> str:
        """Generate Python test file content."""
        content = [
            "import unittest",
            "from unittest.mock import patch, MagicMock\n",
            f"class {category.title()}Tests(unittest.TestCase):"
        ]

        for test in tests:
            test_name = f"test_{test['name'].lower().replace(' ', '_')}"
            content.extend([
                f"    def {test_name}(self):",
                f'        """',
                f"        {test['description']}",
                f"        Priority: {test.get('priority', 'Medium')}",
                f'        """',
                "        # TODO: Implement test steps",
                "        pass\n"
            ])

        content.extend([
            "if __name__ == '__main__':",
            "    unittest.main()"
        ])

        return "\n".join(content)
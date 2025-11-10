from typing import Dict, Any, List
from .base_agent import BaseAgent
from pathlib import Path

class BusinessAgent(BaseAgent):
    async def process(self, input_data: str) -> str:
        """Process business requirements and analyze them."""
        # Load system prompt if available
        prompt_path = Path(__file__).parent.parent / 'services' / 'prompts' / 'business.txt'
        if not prompt_path.exists():
            raise FileNotFoundError(f"Missing prompt file: {prompt_path}")
        system_prompt = prompt_path.read_text()

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Analyze these project requirements and create a detailed specification: {input_data}"}
        ]
        
        response = self._call_llm_api(messages)
        return response["choices"][0]["message"]["content"]

    def generate_artifacts(self, output_dir: str) -> None:
        """Generate business requirement documents."""
        pass  # Implement artifact generation

class ArchitectureAgent(BaseAgent):
    async def process(self, input_data: str) -> str:
        """Design system architecture based on requirements."""
        # Load architecture prompt from shared prompts
        prompt_path = Path(__file__).parent.parent / 'services' / 'prompts' / 'architecture.txt'
        if not prompt_path.exists():
            raise FileNotFoundError(f"Missing prompt file: {prompt_path}")
        system_prompt = prompt_path.read_text()

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Design a complete system architecture for these requirements: {input_data}"}
        ]
        
        response = self._call_llm_api(messages)
        return response["choices"][0]["message"]["content"]

    def generate_artifacts(self, output_dir: str) -> None:
        """Generate architecture diagrams and documentation."""
        pass  # Implement artifact generation

class DeveloperAgent(BaseAgent):
    async def process(self, input_data: str) -> str:
        """Implement code based on architecture."""
        prompt_path = Path(__file__).parent.parent / 'services' / 'prompts' / 'developer.txt'
        if not prompt_path.exists():
            raise FileNotFoundError(f"Missing prompt file: {prompt_path}")
        system_prompt = prompt_path.read_text()

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Implement the code for this architecture or specification: {input_data}"}
        ]
        
        response = self._call_llm_api(messages)
        return response["choices"][0]["message"]["content"]

    def generate_artifacts(self, output_dir: str) -> None:
        """Generate implementation code."""
        pass  # Implement artifact generation

class QAAgent(BaseAgent):
    async def process(self, input_data: str) -> str:
        """Generate and run tests."""
        prompt_path = Path(__file__).parent.parent / 'services' / 'prompts' / 'qa.txt'
        if not prompt_path.exists():
            raise FileNotFoundError(f"Missing prompt file: {prompt_path}")
        system_prompt = prompt_path.read_text()

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Create a test plan and test cases for this implementation: {input_data}"}
        ]
        
        response = self._call_llm_api(messages)
        return response["choices"][0]["message"]["content"]

    def generate_artifacts(self, output_dir: str) -> None:
        """Generate test cases and results."""
        pass  # Implement artifact generation

class AuditAgent(BaseAgent):
    async def process(self, input_data: str) -> str:
        """Review code quality and compliance."""
        prompt_path = Path(__file__).parent.parent / 'services' / 'prompts' / 'audit.txt'
        if not prompt_path.exists():
            raise FileNotFoundError(f"Missing prompt file: {prompt_path}")
        system_prompt = prompt_path.read_text()

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Perform a code audit and find improvements for: {input_data}"}
        ]
        
        response = self._call_llm_api(messages)
        return response["choices"][0]["message"]["content"]

    def generate_artifacts(self, output_dir: str) -> None:
        """Generate audit reports."""
        pass  # Implement artifact generation

class DocumentationAgent(BaseAgent):
    async def process(self, input_data: str) -> str:
        """Generate documentation."""
        prompt_path = Path(__file__).parent.parent / 'services' / 'prompts' / 'documentation.txt'
        if not prompt_path.exists():
            raise FileNotFoundError(f"Missing prompt file: {prompt_path}")
        system_prompt = prompt_path.read_text()

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Create complete project documentation for: {input_data}"}
        ]
        
        response = self._call_llm_api(messages)
        return response["choices"][0]["message"]["content"]

    def generate_artifacts(self, output_dir: str) -> None:
        """Generate documentation files."""
        pass  # Implement artifact generation
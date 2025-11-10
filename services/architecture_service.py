"""Architecture design service."""
from pathlib import Path
from typing import Dict, Any
import json
import aiohttp
from .base_service import BaseAgentService

class ArchitectureService(BaseAgentService):
    import re
    
    @property
    def agent_type(self) -> str:
        return "architecture"

    def clean_json_string(self, text: str) -> str:
        """Clean a string and normalize Unicode characters."""
        if not isinstance(text, str):
            return text

        # Remove code fences and trim
        text = text.replace('```json', '').replace('```', '')
        text = text.strip()

        # Remove comments (both single-line and multi-line)
        import re
        text = re.sub(r'//.*$', '', text, flags=re.MULTILINE)  # Remove single line comments
        text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)  # Remove multi-line comments

        # Replace Unicode spaces and special characters with ASCII equivalents
        replacements = {
            '\u202f': ' ',    # narrow no-break space
            '\u00a0': ' ',    # no-break space
            '\u2011': '-',    # non-breaking hyphen
            '\u2013': '-',    # en dash
            '\u2014': '-',    # em dash
            '\u2018': "'",    # left single quotation
            '\u2019': "'",    # right single quotation
            '\u201c': '"',    # left double quotation
            '\u201d': '"',    # right double quotation
            '\u2265': '>=',   # greater than or equal to
            '\u2264': '<=',   # less than or equal to
            '\u221e': 'inf',  # infinity
            '\u2026': '...',  # ellipsis
            '\u2192': '->',   # right arrow
            '\u2194': '<->',  # left-right arrow
        }
        for unicode_char, ascii_char in replacements.items():
            text = text.replace(unicode_char, ascii_char)

        # Fix common JSON syntax issues
        replacements = [
            ('",,"', '","'),          # Fix double commas
            ('}{', '},{'),            # Add comma between objects
            (']"', '],"'),           # Add comma after array
            ('"`', '"'),             # Remove backticks
            ('`', ''),               # Remove backticks
            ('long,', '"long",'),    # Fix type literals
            ('long}', '"long"}'),    # Fix type literals
            ('long]', '"long"]'),    # Fix type literals
            ('UUID,', '"UUID",'),    # Fix type literals
            ('UUID}', '"UUID"}'),    # Fix type literals
            ('UUID]', '"UUID"]'),    # Fix type literals
            ('boolean,', '"boolean",'), # Fix type literals
            ('boolean}', '"boolean"}'), # Fix type literals
            ('boolean]', '"boolean"]'), # Fix type literals
            ('void,', '"void",'),      # Fix type literals
            ('void}', '"void"}'),      # Fix type literals
            ('void]', '"void"]'),      # Fix type literals
            ('object,', '"object",'),  # Fix type literals
            ('object}', '"object"}'),  # Fix type literals
            ('object]', '"object"]'),  # Fix type literals
            ('Promise<', '"Promise<'),  # Fix Promise types
            ('Promise>', 'Promise>"'),  # Fix Promise types
            ('List<', '"List<'),       # Fix List types
            ('List>', 'List>"'),       # Fix List types
            ('Chat & File', '"Chat and File"'),  # Fix invalid property names
            ('& ', 'and '),            # Fix ampersands in strings
        ]
        for old, new in replacements:
            text = text.replace(old, new)

        # Handle escaped quotes properly
        text = text.replace('\\"', '"').replace("\\'", "'")
        
        # Remove any remaining invalid JSON characters
        text = ''.join(c for c in text if c.isprintable())

        # Remove any trailing commas before closing braces/brackets
        text = re.sub(r',(\s*[}\]])', r'\1', text)

        # Remove any markdown footer after the JSON
        if '**Key Highlights**' in text:
            text = text.split('**Key Highlights**')[0].strip()

        return text

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

        # Load system prompt from external file to avoid embedding raw prompt text in code
        prompt_path = Path(__file__).parent / 'prompts' / 'architecture.txt'
        if not prompt_path.exists():
            raise FileNotFoundError(f"Missing prompt file: {prompt_path}")
        system_prompt = prompt_path.read_text()

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Design a complete system architecture for these requirements: {requirements}"}
        ]
        
        response = await self._call_llm_api(messages)
        content = response["choices"][0]["message"]["content"]
        
        # Clean and parse JSON
        try:
            # First clean the content
            cleaned_content = self.clean_json_string(content)
            
            # Try to parse the cleaned content
            try:
                result = json.loads(cleaned_content)
            except json.JSONDecodeError as e:
                # If parsing fails, try more aggressive cleaning
                print(f"Initial parsing failed: {str(e)}")
                cleaned_content = re.sub(r',\s*([}\]])', r'\1', cleaned_content)
                result = json.loads(cleaned_content)

            return {
                "status": "success",
                "architecture": result,
                "format_version": "1.0"
            }
        except Exception as e:
            print(f"Error processing JSON: {str(e)}")
            return {
                "status": "error",
                "error": f"Invalid JSON format: {str(e)}",
                "raw_content": content
            }

    def save_artifacts(self, result: Dict[str, Any]) -> None:
        """Generate and save architecture documentation."""
        if result["status"] != "success":
            return

        try:
            # If the architecture is already a dict, convert it to JSON string first
            if isinstance(result["architecture"], dict):
                arch_json = json.dumps(result["architecture"])
            else:
                arch_json = result["architecture"]

            # Clean the JSON string
            cleaned_json = self.clean_json_string(arch_json)

            # Parse the cleaned JSON
            try:
                cleaned_arch = json.loads(cleaned_json)
            except json.JSONDecodeError as e:
                print(f"Error parsing cleaned JSON: {str(e)}")
                # If parsing fails, try a more aggressive cleaning
                cleaned_json = re.sub(r',\s*([}\]])', r'\1', cleaned_json)
                cleaned_arch = json.loads(cleaned_json)

            # Save the cleaned architecture
            arch_path = self.get_artifact_path("architecture.json")
            with open(arch_path, 'w') as f:
                json.dump(cleaned_arch, f, indent=2)

        except Exception as e:
            print(f"Error saving artifacts: {str(e)}")
            # Save the raw content for debugging
            raw_path = self.get_artifact_path("architecture_raw.txt")
            with open(raw_path, 'w') as f:
                f.write(str(result["architecture"]))

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
"""Developer implementation service."""
from pathlib import Path
from typing import Dict, Any, Optional
import json
import re
import aiohttp
from .base_service import BaseAgentService

class DeveloperService(BaseAgentService):
    @property
    def agent_type(self) -> str:
        return "developer"
        
    def clean_json_string(self, text: str) -> str:
        """Clean a string and balance braces."""
        # Handle code blocks
        text = text.replace('```json', '').replace('```', '')
        
        # Handle special characters
        chars = {
            '\\"': '"', "\\'": "'",
            '\\u201c': '"', '\\u201d': '"',  # Quotes
            '\\u2018': "'", '\\u2019': "'",  # Apostrophes  
            '\\u2011': '-', '\\u2012': '-',  # Hyphens
            '\\u2013': '-', '\\u2014': '--', # Dashes
            '\\u2026': '...', # Ellipsis
            '\\u2022': '*',   # Bullet
            '\\u2500': '-', '\\u2502': '|',  # Box drawing
            '\\u251c': '+', '\\u2514': '+'   # Box drawing
        }
        
        for old, new in chars.items():
            text = text.replace(old, new)
        
        # Balance braces
        open_count = text.count('{')
        close_count = text.count('}')
        
        if open_count > close_count:
            text = text.strip() + ('}' * (open_count - close_count))
        
        return text.strip()
        
    async def parse_input(self, input_data: str) -> Optional[Dict]:
        """Parse input from string, file or URL."""
        if not isinstance(input_data, str):
            return input_data
            
        try:
            return json.loads(input_data)
        except json.JSONDecodeError:
            if input_data.startswith(('http://', 'https://')):
                async with aiohttp.ClientSession() as session:
                    async with session.get(input_data) as response:
                        return await response.json()
                        
            try:
                path = Path(input_data)
                if path.is_file():
                    return json.loads(path.read_text())
            except:
                pass
                
        return None
        
    def extract_json(self, content: str) -> Optional[Dict]:
        """Extract valid JSON from content."""
        # Clean the content
        content = self.clean_json_string(content)
        
        # Try parsing directly
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
            
        # Try JSON code blocks
        matches = re.findall(r'```json\s*(.*?)\s*```', content, re.DOTALL)
        for match in matches:
            try:
                return json.loads(self.clean_json_string(match))
            except json.JSONDecodeError:
                continue
                
        # Try finding JSON objects
        matches = re.findall(r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}', content, re.DOTALL)
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue
                
        return None
        
    async def process(self, input_data: str) -> Dict[str, Any]:
        """Process architecture and generate implementation."""
        try:
            # Parse input
            parsed_input = await self.parse_input(input_data)
            if not parsed_input:
                return {
                    "status": "error",
                    "error": "Could not parse input data"
                }
                
            # Prepare prompt
            messages = [
                {
                    "role": "system", 
                    "content": """You are an expert Software Developer.
                    Generate implementation including:
                    1. Project Structure
                    2. Core Components 
                    3. API Implementations
                    4. Database Models
                    5. Utility Functions
                    6. Configuration Files
                    
                    Format the output as structured JSON with code implementations."""
                },
                {
                    "role": "user",
                    "content": f"Implement the code for this architecture: {json.dumps(parsed_input)}"
                }
            ]

            # Get LLM response
            response = await self._call_llm_api(messages)
            content = response["choices"][0]["message"]["content"]
            
            # Extract JSON
            implementation = self.extract_json(content)
            if not implementation:
                return {
                    "status": "error",
                    "error": "Could not extract valid JSON from response",
                    "raw_content": content
                }
                
            return {
                "status": "success",
                "implementation": implementation,
                "format_version": "1.0"
            }

        except Exception as e:
            return {
                "status": "error", 
                "error": str(e)
            }\"', '"').replace("\\'", "'")
                s = s.replace('\\u201c', '"').replace('\\u201d', '"')
                s = s.replace('\\u2018', "'").replace('\\u2019', "'")
                s = s.replace('\\u2011', '-').replace('\\u2012', '-')
                s = s.replace('\\u2013', '-').replace('\\u2014', '--')
                s = s.replace('\\u2026', '...').replace('\\u2022', '*')
                s = s.replace('\\u2500', '-').replace('\\u2502', '|')
                s = s.replace('\\u251c', '+').replace('\\u2514', '+')
                
                # Balance braces
                open_braces = s.count('{')
                close_braces = s.count('}')
                
                if open_braces > close_braces:
                    s += "}" * (open_braces - close_braces)
                elif close_braces > open_braces:
                    while close_braces > open_braces and s.endswith("}"):
                        s = s[:-1]
                        close_braces -= 1
                
                return s.strip()            # Debug output
            print("\nOriginal content:", content[:200], "...")
            cleaned_content = clean_json_string(content)
            print("\nCleaned content:", cleaned_content[:200], "...")
            
            # Try parsing as JSON
            try:
                # First try the full cleaned content if it looks like JSON
                if cleaned_content.strip().startswith("{") and cleaned_content.strip().endswith("}"):
                    try:
                        result = json.loads(cleaned_content)
                        return {
                            "status": "success",
                            "implementation": result,
                            "format_version": "1.0"
                        }
                    except json.JSONDecodeError:
                        pass

                # Search for ```json blocks
                json_blocks = re.findall(r'```json\s*(.*?)\s*```', content, re.DOTALL)
                for block in json_blocks:
                    try:
                        result = json.loads(clean_json_string(block))
                        return {
                            "status": "success",
                            "implementation": result,
                            "format_version": "1.0"
                        }
                    except json.JSONDecodeError:
                        continue
                        
                # Look for JSON objects
                objects = re.findall(r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}', cleaned_content, re.DOTALL)
                for obj in objects:
                    try:
                        result = json.loads(obj)
                        return {
                            "status": "success",
                            "implementation": result,
                            "format_version": "1.0"
                        }
                    except json.JSONDecodeError:
                        continue
                        
                raise json.JSONDecodeError("No valid JSON found", content, 0)
                
            except json.JSONDecodeError as e:
                return {
                    "status": "error",
                    "error": f"Invalid JSON format: {str(e)}",
                    "raw_content": cleaned_content
                }
                
        except Exception as e:
            import traceback
            print("\nDetailed error information:")
            print(traceback.format_exc())
            return {
                "status": "error",
                "error": str(e),
                "raw_content": input_data
            }\"', '"')
                s = s.replace("\\'", "'")
                s = s.replace('\\u201c', '"')  # Left double quote
                s = s.replace('\\u201d', '"')  # Right double quote
                s = s.replace('\\u2018', "'")  # Left single quote
                s = s.replace('\\u2019', "'")  # Right single quote
                
                # Fix common punctuation
                s = s.replace('\\u2011', '-')  # Non-breaking hyphen
                s = s.replace('\\u2012', '-')  # Figure dash 
                s = s.replace('\\u2013', '-')  # En dash
                s = s.replace('\\u2014', '--') # Em dash
                s = s.replace('\\u2026', '...') # Ellipsis

                # Fix fancy characters
                s = s.replace('\\u2022', '*')  # Bullet
                s = s.replace('\\u2500', '-')  # Box drawings
                s = s.replace('\\u2502', '|')
                s = s.replace('\\u251c', '+')
                s = s.replace('\\u2514', '+')

                return s
                
            def clean_json(content):
                """Recursively clean problematic characters from JSON content."""
                if isinstance(content, str):
                    cleaned = clean_json_string(content)
                    
                    # Balance braces if needed
                    open_braces = cleaned.count("{")
                    close_braces = cleaned.count("}")
                    
                    if open_braces > close_braces:
                        # Add missing closing braces
                        cleaned += "}" * (open_braces - close_braces)
                    elif close_braces > open_braces:
                        # Remove extra closing braces from the end
                        while close_braces > open_braces and cleaned.endswith("}"):
                            cleaned = cleaned[:-1]
                            close_braces -= 1
                            
                    return cleaned
                    
                elif isinstance(content, list):
                    return [clean_json(item) for item in content]
                    
                elif isinstance(content, dict):
                    return {
                        clean_json(key): clean_json(value)
                        for key, value in content.items()
                    }
                    
                else:
                    return content

            # Try extracting JSON blocks from markdown first
            json_pattern = r'```json\s*(.*?)\s*```'
            matches = re.findall(json_pattern, content, re.DOTALL)
            if matches:
                for match in matches:
                    try:
                        data = json.loads(match)
                        return json.dumps(clean_json(data))
                    except json.JSONDecodeError:
                        continue

            # Try to find complete JSON objects
            object_pattern = r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}'
            matches = re.findall(object_pattern, content, re.DOTALL)
            max_object = None
            max_length = 0
            
            for match in matches:
                try:
                    data = json.loads(match)
                    if len(match) > max_length:
                        max_length = len(match)
                        max_object = data
                except json.JSONDecodeError:
                    continue
                    
            if max_object:
                return json.dumps(clean_json(max_object))
                
            # Clean and try the whole content
            try:
                cleaned = clean_json_string(content)
                data = json.loads(cleaned)
                return json.dumps(clean_json(data))
            except json.JSONDecodeError:
                # Return raw content as last resort
                return content

            content = clean_json(content)
            
            # Original content for debugging
            print("\nOriginal content:", content[:200], "...")
            
            # Clean and process content
            content = clean_json(content)
            print("\nCleaned content:", content[:200], "...")
            
            # Log brace counts
            open_braces = content.count("{")
            close_braces = content.count("}")
            print(f"\nBrace counts - Open: {open_braces}, Close: {close_braces}")
            
            try:
                # Try to validate JSON structure
                print("\nValidating JSON structure...")
                
                if not content.strip().startswith("{"):
                    print("Content does not start with {")
                    raise json.JSONDecodeError("Does not start with {", content, 0)
                    
                if not content.strip().endswith("}"):
                    print("Content does not end with }")
                    raise json.JSONDecodeError("Does not end with }", content, len(content))
                
                # Try parsing the cleaned content
                result = json.loads(content)
                print("JSON validation successful!")
                return {
                    "status": "success",
                    "implementation": result,
                    "format_version": "1.0"
                }
            except json.JSONDecodeError as e:
                # If that fails, try harder
                try:
                    # Replace newlines and extra spaces
                    content = re.sub(r'\s+', ' ', content)
                    
                    # Find deepest valid JSON
                    max_object = None
                    max_length = 0
                    for i in range(len(content)):
                        if content[i] == '{':
                            for j in range(i+1, len(content)):
                                if content[j] == '}':
                                    try:
                                        obj = content[i:j+1]
                                        result = json.loads(obj)
                                        if len(obj) > max_length:
                                            max_length = len(obj)
                                            max_object = result
                                    except:
                                        continue
                    
                    if max_object:
                        return {
                            "status": "success",
                            "implementation": max_object,
                            "format_version": "1.0"
                        }
                except:
                    pass
                
                return {
                    "status": "error",
                    "error": f"Invalid JSON: {str(e)}",
                    "raw_content": content[:1000] + "..." if len(content) > 1000 else content
                }

                try:
                    response = await self._call_llm_api(messages)
                    print("\nLLM API Response:", json.dumps(response, indent=2))
                    content = response["choices"][0]["message"]["content"]
                    
            # Clean up the content
            print("\nOriginal content:", content[:200], "...")
            content = clean_json(content)
            print("\nCleaned content:", content[:200], "...")
            
            # Log brace counts 
            open_braces = content.count("{")
            close_braces = content.count("}")
            print(f"\nBrace counts - Open: {open_braces}, Close: {close_braces}")                    try:
                        # Try to validate JSON structure
                        print("\nValidating JSON structure...")
                        
                        if not content.strip().startswith("{"):
                            print("Content does not start with {")
                            raise json.JSONDecodeError("Does not start with {", content, 0)
                            
                        if not content.strip().endswith("}"):
                            print("Content does not end with }")
                            raise json.JSONDecodeError("Does not end with }", content, len(content))
                        
                        result = json.loads(content)
                        print("JSON validation successful!")
                        return {
                            "status": "success",
                            "implementation": result,
                            "format_version": "1.0"
                        }
                    except json.JSONDecodeError as e:
                        # Try harder to find valid JSON
                        try:
                            content = content.replace("\n", " ").strip()
                            open_braces = content.count("{")
                            close_braces = content.count("}")
                            
                            # Complete missing braces
                            if open_braces > close_braces:
                                content += "}" * (open_braces - close_braces)
                                
                            result = json.loads(content)
                            return {
                                "status": "success", 
                                "implementation": result,
                                "format_version": "1.0"
                            }
                        except:
                            pass
                            
                        return {
                            "status": "error",
                            "error": f"Invalid JSON format: {str(e)}",
                            "raw_content": content
                        }
                except Exception as e:
                    print("\nError in LLM API call:", str(e))
                    raise
                
        except Exception as e:
            import traceback
            print("\nDetailed error information:")
            print(traceback.format_exc())
            return {
                "status": "error",
                "error": str(e),
                "raw_content": input_data
            }

    def save_artifacts(self, result: Dict[str, Any]) -> None:
        """Generate and save implementation files."""
        if result["status"] != "success":
            return

        impl = result["implementation"]
        
        # Save raw implementation
        impl_path = self.get_artifact_path("implementation.json")
        with open(impl_path, 'w') as f:
            json.dump(impl, f, indent=2)

        # Create src directory
        src_dir = self.output_dir / "src"
        src_dir.mkdir(exist_ok=True)

        # Save source files
        if "files" in impl:
            for file_info in impl["files"]:
                path = src_dir / file_info["path"]
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(file_info["content"])

        # Save package file
        if "package" in impl:
            pkg_path = self.output_dir / "package.json"
            with open(pkg_path, 'w') as f:
                json.dump(impl["package"], f, indent=2)

        # Save config files
        if "config" in impl:
            config_dir = self.output_dir / "config" 
            config_dir.mkdir(exist_ok=True)
            
            for name, data in impl["config"].items():
                path = config_dir / f"{name}.json"
                with open(path, 'w') as f:
                    json.dump(data, f, indent=2)

        # Generate README
        readme = [
            "# Implementation\n",
            "## Project Structure\n",
            "```",
            self._generate_tree_structure(src_dir),
            "```\n", 
            "## Setup\n",
            "```bash",
            "npm install  # or pip install -r requirements.txt",
            "```\n",
            "## Running\n", 
            "```bash",
            "npm start  # or python main.py",
            "```"
        ]

        readme_path = self.get_artifact_path("README.md")
        with open(readme_path, 'w') as f:
            f.write("\n".join(readme))

    def _generate_tree_structure(self, path: Path, prefix: str = "") -> str:
        """Generate tree view of directory structure."""
        if not path.exists():
            return ""
            
        tree = []
        entries = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name))
        
        for i, entry in enumerate(entries):
            is_last = i == len(entries) - 1
            node = "└── " if is_last else "├── "
            tree.append(f"{prefix}{node}{entry.name}")
            
            if entry.is_dir():
                next_prefix = prefix + ("    " if is_last else "│   ")
                tree.append(self._generate_tree_structure(entry, next_prefix))
                
        return "\n".join(tree)
"""Developer implementation service."""
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import json
import re
import aiohttp
from pathlib import Path
from .base_service import BaseAgentService


class DeveloperService(BaseAgentService):
    def load_prompt(self, prompt_name: str) -> str:
        """Load a prompt from the prompts directory."""
        prompt_path = Path(__file__).parent / 'prompts' / f'{prompt_name}.txt'
        try:
            return prompt_path.read_text()
        except FileNotFoundError:
            # Default prompt if file not found
            return (
                "You are an expert Software Developer. Generate implementation files based on "
                "the provided architecture and specifications. For each file use the format:\n\n"
                "### File: path/to/file.ext\n"
                "```\n"
                "file content\n"
                "```\n\n"
                "Generate complete, production-ready code files following best practices. "
                "Include proper error handling, documentation, and tests where appropriate."
            )
    def get_project_path(self) -> Path:
        """Return the project base path for the current project."""
        return Path("projects") / self.project_name
    @property
    def agent_type(self) -> str:
        return "developer"

    def clean_json_string(self, text: str) -> str:
        """Clean a string and balance braces."""
        if not isinstance(text, str):
            return text

        # Remove code fences and trim
        text = text.replace('```json', '').replace('```', '')
        text = text.strip()

        # Basic escape fixes
        text = text.replace('\\"', '"').replace("\\'", "'")

        # Balance braces
        open_count = text.count('{')
        close_count = text.count('}')
        if open_count > close_count:
            text = text + ('}' * (open_count - close_count))

        return text

    async def parse_input(self, input_data: Union[str, Dict]) -> Optional[Dict]:
        """Parse input from string, file or URL."""
        if isinstance(input_data, dict):
            return input_data

        if not isinstance(input_data, str):
            return None

        # Try direct JSON
        try:
            return json.loads(input_data)
        except json.JSONDecodeError:
            pass

        # Try URL
        if input_data.startswith(('http://', 'https://')):
            async with aiohttp.ClientSession() as session:
                async with session.get(input_data) as response:
                    return await response.json()

        # Try file path
        try:
            p = Path(input_data)
            if p.is_file():
                return json.loads(p.read_text())
        except Exception:
            pass

        return None

    def extract_json(self, content: str) -> Optional[Dict]:
        """Extract JSON object from a text blob."""
        if not isinstance(content, str):
            return None

        clean = self.clean_json_string(content)

        # Try full parse
        try:
            return json.loads(clean)
        except json.JSONDecodeError:
            pass

        # Try json code blocks
        blocks = re.findall(r'```json\\s*(.*?)\\s*```', content, re.DOTALL)
        for b in blocks:
            try:
                return json.loads(self.clean_json_string(b))
            except json.JSONDecodeError:
                continue

        # Try to find the largest JSON object substring
        objs = re.findall(r'\\{(?:[^{}]|(?:\\{[^{}]*\\}))*\\}', content, re.DOTALL)
        max_obj = None
        max_len = 0
        for o in objs:
            try:
                parsed = json.loads(o)
                if len(o) > max_len:
                    max_len = len(o)
                    max_obj = parsed
            except json.JSONDecodeError:
                continue

        return max_obj

    def is_likely_truncated(self, text: str) -> bool:
        """Heuristic checks to detect if an LLM response was truncated.

        Returns True if common truncation signs are found (unclosed code fence,
        unbalanced braces, or an abrupt ending character).
        """
        if not text or not isinstance(text, str):
            return False

        # Unclosed fenced code block
        if text.count('```') % 2 != 0:
            return True

        s = text.rstrip()
        if not s:
            return False

        last_char = s[-1]
        # If ends with these characters it's more likely complete
        if last_char in ('\n', '}', ']', '>', ';', '"', "'", ')'):
            pass
        else:
            return True

        # Unbalanced braces is a good sign of truncation for code-like outputs
        if text.count('{') > text.count('}'):
            return True

        return False

    async def _recover_truncated_response(self, initial_text: str, base_messages: list, max_attempts: int = 3) -> str:
        """Attempt to recover a truncated LLM response by asking for continuation.

        Appends continuation responses to the initial_text. Stops early if heuristics
        indicate the response is complete.
        """
        full = initial_text
        for attempt in range(max_attempts):
            if not self.is_likely_truncated(full):
                break

            follow_up = (
                "The previous response was truncated. Continue the response from where it stopped, "
                "using the same format. Do NOT repeat file contents already fully returned; only provide the continuation."
            )

            follow_messages = base_messages + [{"role": "user", "content": follow_up}]
            try:
                resp = await self._call_llm_api(follow_messages)
                addition = resp.get("choices", [])[0].get("message", {}).get("content", "")
                if not addition:
                    break
                # Append and continue
                full = full + "\n" + addition
            except Exception:
                break

        return full

    def save_implementation_files(self, implementation: Dict[str, str], project_path: Path) -> List[str]:
        """Save implementation files to the project directory."""
        saved_files = []
        developer_path = project_path / "developer"
        developer_path.mkdir(exist_ok=True)

        for filename, content in implementation.items():
            # Create subdirectories if needed
            file_path = developer_path / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write the file
            file_path.write_text(content)
            saved_files.append(str(file_path))

        return saved_files

    async def process(self, input_data: Union[str, Dict]) -> Dict[str, Any]:
        """Process input and call LLM to generate implementation files."""
        try:
            # Parse input data
            parsed_input = await self.parse_input(input_data)
            if not parsed_input:
                return {"status": "error", "error": "Could not parse input data"}

            # Get architecture and specifications
            messages = [
                {
                    "role": "system", 
                    "content": self.load_prompt("developer")
                },
                {
                    "role": "user", 
                    "content": (
                        "Generate the implementation files based on the following architecture and specifications. "
                        "Format each file with:\n\n"
                        "### File: path/to/file.ext\n"
                        "```\n"
                        "file content\n"
                        "```\n\n"
                        f"Architecture: {json.dumps(parsed_input.get('architecture', {}))}\n"
                        f"Specifications: {json.dumps(parsed_input.get('specifications', {}))}"
                    )
                }
            ]

            # Call LLM to generate implementation
            response = await self._call_llm_api(messages)
            response_text = response["choices"][0]["message"]["content"]

            # If response looks truncated, try to recover by requesting continuation
            response_text = await self._recover_truncated_response(response_text, messages)
            
            # Parse the files from the response
            files = []
            current_file = None
            content_lines = []
            
            for line in response_text.split('\n'):
                if line.startswith('### File: '):
                    # Save previous file if exists
                    if current_file and content_lines:
                        files.append({
                            'path': current_file,
                            'content': '\n'.join(content_lines)
                        })
                    # Start new file
                    current_file = line[9:].strip()
                    content_lines = []
                elif line.startswith('```'):
                    continue
                elif current_file:
                    content_lines.append(line)
            
            # Save last file
            if current_file and content_lines:
                files.append({
                    'path': current_file,
                    'content': '\n'.join(content_lines)
                })

            if not files:
                return {
                    "status": "error",
                    "error": "No valid files found in response",
                    "raw_content": response_text
                }

            # If some file contents look truncated, request continuation per-file
            for idx, f in enumerate(files):
                content = f.get('content', '')
                if self.is_likely_truncated(content):
                    follow_up = (
                        f"The file `{f['path']}` appears truncated. Please return the COMPLETE content of this file only, "
                        "in the same plain format (no surrounding JSON). Do not include other files."
                    )
                    try:
                        resp = await self._call_llm_api(messages + [{"role": "user", "content": follow_up}])
                        more = resp.get("choices", [])[0].get("message", {}).get("content", "")
                        # Try to extract the code block or the plain content
                        if more:
                            # If returned with fences, strip them
                            if more.strip().startswith('```') and more.strip().endswith('```'):
                                more = '\n'.join(more.strip().split('\n')[1:-1])
                            files[idx]['content'] = files[idx]['content'] + '\n' + more
                    except Exception:
                        # ignore and proceed; we'll save what we have
                        pass

            # Save the files
            project_path = self.get_project_path()
            saved_files = []
            
            for file_info in files:
                file_path = project_path / "developer" / file_info['path']
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(file_info['content'])
                saved_files.append(str(file_path))

            return {
                "status": "success",
                "files": saved_files,
                "file_count": len(saved_files)
            }
        except Exception as e:
            return {
                "status": "error", 
                "error": str(e)
            }

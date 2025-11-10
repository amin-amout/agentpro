"""Developer implementation service."""
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import json
import re
import aiohttp
from .base_service import BaseAgentService


class DeveloperService(BaseAgentService):
    def load_prompt(self, prompt_name: str) -> str:
        """Load a prompt from the prompts directory."""
        prompt_path = Path(__file__).parent / 'prompts' / f'{prompt_name}.txt'
        if not prompt_path.exists():
            raise FileNotFoundError(f"Missing prompt file: {prompt_path}. Create it under services/prompts/")

        return prompt_path.read_text()

    def get_project_path(self) -> Path:
        """Return the project base path for the current project."""
        return Path("projects") / self.project_name

    @property
    def agent_type(self) -> str:
        return "developer"

    def is_likely_truncated(self, text: str) -> bool:
        """Heuristic checks to detect if an LLM response was truncated."""
        if not text or not isinstance(text, str):
            return False

        # Unclosed fenced code block
        if text.count('```') % 2 != 0:
            return True

        s = text.rstrip()
        if not s:
            return False

        last_char = s[-1]
        if last_char in ('\n', '}', ']', '>', ';', '"', "'", ')'):
            pass
        else:
            return True

        # Unbalanced braces
        if text.count('{') > text.count('}'):
            return True

        return False

    async def _recover_truncated_response(self, initial_text: str, base_messages: list, max_attempts: int = 2) -> str:
        """Attempt to recover a truncated LLM response by asking for continuation."""
        full = initial_text
        for attempt in range(max_attempts):
            if not self.is_likely_truncated(full):
                break

            follow_up = "Continue the previous response from where it stopped. Only provide the continuation."
            follow_messages = base_messages + [{"role": "user", "content": follow_up}]
            try:
                resp = await self._call_llm_api(follow_messages)
                addition = resp.get("choices", [])[0].get("message", {}).get("content", "")
                if not addition:
                    break
                full = full + "\n" + addition
                await asyncio.sleep(1)  # Delay between continuation requests
            except Exception:
                break

        return full

    async def process(self, input_data: Union[str, Dict]) -> Dict[str, Any]:
        """Process input and generate implementation files (per-file approach)."""
        try:
            # Parse input
            if isinstance(input_data, str):
                try:
                    parsed_input = json.loads(input_data)
                except json.JSONDecodeError:
                    p = Path(input_data)
                    if p.is_file():
                        parsed_input = json.loads(p.read_text())
                    else:
                        return {"status": "error", "error": "Could not parse input"}
            else:
                parsed_input = input_data

            if not parsed_input:
                return {"status": "error", "error": "No input data"}

            # Extract modules from architecture
            project_path = self.get_project_path()
            modules = []
            ca = parsed_input.get('ComponentArchitecture') or {}
            if isinstance(ca, dict):
                modules = ca.get('modules', [])
            elif isinstance(ca, list):
                modules = ca

            # Define files to generate
            file_specs = [
                {"path": "index.html", "role": "entry_html"},
                {"path": "styles.css", "role": "styles"},
                {"path": "main.js", "role": "entry_js"}
            ]

            # Add module files
            for m in modules:
                name = m.get('name') if isinstance(m, dict) else str(m)
                if not name:
                    continue
                fname = ''.join(ch for ch in name if ch.isalnum())
                if not fname:
                    continue
                fname = fname[0].lower() + fname[1:] if len(fname) > 1 else fname.lower()
                file_specs.append({"path": f"src/{fname}.js", "module": m})

            system_prompt = self.load_prompt("developer")
            saved_files = []

            # Generate files one by one
            for idx, spec in enumerate(file_specs):
                target = spec['path']
                user_content = (
                    f"Generate the COMPLETE content for '{target}'.\n"
                    "Return ONLY the file content, no markdown or JSON.\n\n"
                    f"Architecture: {json.dumps(parsed_input.get('architecture', {}))}\n"
                    f"Specifications: {json.dumps(parsed_input.get('specifications', {}))}\n"
                )
                if spec.get('module'):
                    user_content += "Module: " + json.dumps(spec['module']) + "\n"

                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ]

                # Add delay before each call (except first)
                # Exponential backoff: increase delay progressively
                if idx > 0:
                    delay = min(15, 5 + (idx * 2))  # 5s, 7s, 9s, ... up to 15s
                    await asyncio.sleep(delay)

                try:
                    resp = await self._call_llm_api(messages)
                    text = resp.get('choices', [])[0].get('message', {}).get('content', '')
                except Exception as e:
                    print(f"Error generating {target}: {e}")
                    continue

                if not text:
                    continue

                # Try to recover if truncated
                text = await self._recover_truncated_response(text, messages)

                # Strip fences
                stripped = text.strip()
                if stripped.startswith('```') and stripped.endswith('```'):
                    parts = stripped.split('\n')
                    if len(parts) >= 3:
                        stripped = '\n'.join(parts[1:-1])

                # Final check + one more continuation if needed
                if self.is_likely_truncated(stripped):
                    follow = f"File '{target}' is truncated. Return complete content only."
                    try:
                        await asyncio.sleep(1)
                        resp2 = await self._call_llm_api(messages + [{"role": "user", "content": follow}])
                        more = resp2.get('choices', [])[0].get('message', {}).get('content', '')
                        if more:
                            mstrip = more.strip()
                            if mstrip.startswith('```') and mstrip.endswith('```'):
                                parts = mstrip.split('\n')
                                if len(parts) >= 3:
                                    mstrip = '\n'.join(parts[1:-1])
                            stripped = stripped + '\n' + mstrip
                    except Exception:
                        pass

                # Save file
                file_path = project_path / 'developer' / target
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(stripped)
                saved_files.append(str(file_path))

            if not saved_files:
                return {"status": "error", "error": "No files generated"}

            return {"status": "success", "files": saved_files, "file_count": len(saved_files)}

        except Exception as e:
            return {"status": "error", "error": str(e)}

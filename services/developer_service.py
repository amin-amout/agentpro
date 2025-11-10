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

    async def parse_input(self, input_data: str) -> Optional[Dict]:
        """Parse input from string, file or URL."""
        if not isinstance(input_data, str):
            return input_data

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

    async def process(self, input_data: str) -> Dict[str, Any]:
        """Process input and call LLM to generate implementation JSON."""
        try:
            parsed_input = await self.parse_input(input_data)
            if not parsed_input:
                return {"status": "error", "error": "Could not parse input data"}

            messages = [
                {"role": "system", "content": (
                    "You are an expert Software Developer. Generate implementation as structured JSON with code files."
                )},
                {"role": "user", "content": f"Implement the code for this architecture: {json.dumps(parsed_input)}"}
            ]

            response = await self._call_llm_api(messages)
            content = response.get("choices", [])[0].get("message", {}).get("content", "")

            implementation = self.extract_json(content)
            if not implementation:
                return {"status": "error", "error": "Could not extract valid JSON from response", "raw_content": content}

            return {"status": "success", "implementation": implementation, "format_version": "1.0"}

        except Exception as e:
            return {"status": "error", "error": str(e)}

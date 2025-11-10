from abc import ABC, abstractmethod
import requests
from typing import Dict, Any, List
from .config import settings

class BaseAgent(ABC):
    @classmethod
    def list_available_models(cls, api_key: str) -> List[str]:
        """List available models from the Groq API."""
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        try:
            response = requests.get(
                "https://api.groq.com/openai/v1/models",
                headers=headers
            )
            if response.ok:
                data = response.json()
                return [model['id'] for model in data.get('data', [])]
            else:
                print(f"Error listing models: {response.text}")
                return []
        except Exception as e:
            print(f"Error connecting to Groq API: {str(e)}")
            return []
    def __init__(self, llm_config: Dict[str, Any]):
        self.api_url = llm_config["api_url"]
        self.api_key = llm_config.get("api_key")
        self.model = llm_config["model"]

    def _call_llm_api(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Make an API call to the LLM endpoint."""
        headers = {
            "Content-Type": "application/json"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        data = {
            "model": self.model,
            "messages": messages,
            "temperature": settings.TEMPERATURE,
            "max_tokens": settings.MAX_TOKENS,
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            if not response.ok:
                print(f"\nError Response: {response.text}")
                print(f"Request Headers: {headers}")
                print(f"Request Data: {data}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"\nError making API call: {str(e)}")
            raise

    @abstractmethod
    async def process(self, input_data: str) -> str:
        """Process input data and return results."""
        pass

    def generate_artifacts(self, output_dir: str) -> None:
        """Generate agent-specific artifacts in the output directory."""
        pass
        pass
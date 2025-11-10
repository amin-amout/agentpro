"""Base service for all agent services."""
from abc import ABC, abstractmethod
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import json
import aiohttp
import requests
from .communicator import ServiceCommunicator

class BaseAgentService(ABC):
    def __init__(self, project_name: str, config: Optional[Dict[str, Any]] = None) -> None:
        self.project_name = project_name
        self.config = config or self._load_config()
        self.output_dir = Path("projects") / project_name / self.agent_type
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Dependencies between services
        self.dependencies = {
            "architecture": ["business"],
            "developer": ["architecture"],
            "qa": ["developer"],
            "audit": ["developer", "qa"],
            "documentation": ["business", "architecture", "developer", "qa", "audit"]
        }

        # Service ports for REST API communication
        service_ports = {
            "architecture": 5001,
            "developer": 5002,
            "qa": 5003,
            "audit": 5004,
            "documentation": 5005
        }
        
        # Initialize service communication
        self.communicator = ServiceCommunicator(
            self.agent_type,
            project_name,
            service_ports.get(self.agent_type, 5000)
        )
        
        # Register communication callbacks
        self.communicator.on_file_changed(self._handle_file_update)
        self.communicator.on_notification(self._handle_notification)

    @property
    @abstractmethod
    def agent_type(self) -> str:
        """Return the type of agent (e.g., 'business', 'architecture', etc.)"""
        pass

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environment or config file."""
        from dotenv import load_dotenv
        load_dotenv()
        
        # Try loading service-specific config
        config_path = Path("config") / f"{self.agent_type}_config.json"
        if config_path.exists():
            with open(config_path) as f:
                return json.load(f)

        # Fall back to environment variables                
        api_key = os.getenv("LLM_API_KEY")
        if not api_key:
            raise ValueError("LLM_API_KEY environment variable not found")
            
        # Prefer environment variables when a per-service config file is not provided.
        api_url = os.getenv("LLM_API_URL")
        model = os.getenv("DEFAULT_MODEL")
        temperature = os.getenv("TEMPERATURE")
        max_tokens = os.getenv("MAX_TOKENS")

        # Require explicit configuration to avoid embedding defaults in code.
        missing = []
        if not api_key:
            missing.append('LLM_API_KEY')
        if not api_url:
            missing.append('LLM_API_URL')
        if not model:
            missing.append('DEFAULT_MODEL')

        if missing:
            raise ValueError(
                f"Missing required LLM configuration in environment or config file: {', '.join(missing)}"
            )

        return {
            "api_url": api_url,
            "api_key": api_key,
            "model": model,
            "temperature": float(temperature) if temperature is not None else 0.7,
            "max_tokens": int(max_tokens) if max_tokens is not None else 4096,
        }

    async def _call_llm_api(self, messages: list) -> Dict[str, Any]:
        """Make an API call to the LLM endpoint."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config['api_key']}"
        }

        data = {
            "model": self.config["model"],
            "messages": messages,
            "temperature": self.config.get("temperature", 0.7),
            "max_tokens": self.config.get("max_tokens", 4096),
        }

        try:
            timeout = aiohttp.ClientTimeout(total=30)  # 30 second timeout
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(self.config["api_url"], headers=headers, json=data) as response:
                    response.raise_for_status()
                    
                    # Stream response in chunks to handle large responses
                    chunks = []
                    async for chunk in response.content.iter_chunks():
                        chunks.append(chunk[0])
                    
                    # Combine chunks and decode
                    content = b''.join(chunks).decode('utf-8')
                    
                    # Parse JSON response
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError as e:
                        print(f"Error decoding LLM response as JSON: {str(e)}")
                        print("Raw content:", content)
                        raise
        except Exception as e:
            print(f"Error calling LLM API: {str(e)}")
            if 'response' in locals() and hasattr(response, 'text'):
                print(f"Response text: {response.text}")
            raise

    async def _handle_file_update(self, data: Dict[str, Any]):
        """Handle updates from watched files."""
        print(f"\nReceived file update in {self.agent_type} service:")
        print(json.dumps(data, indent=2))
        
        # Check if we should process this update
        if self._should_process_update(data):
            await self.process_update(data)

    async def _handle_notification(self, data: Dict[str, Any]):
        """Handle notifications from other services."""
        print(f"\nReceived notification in {self.agent_type} service:")
        print(json.dumps(data, indent=2))
        
        # Check if we should process this notification
        if self._should_process_update(data):
            await self.process_update(data)

    def _should_process_update(self, data: Dict[str, Any]) -> bool:
        """Check if this service should process the update."""
        # Get the source service from the data
        source = data.get("source")
        if not source:
            return False
            
        # Check if this update is from a dependency
        return source in self.dependencies.get(self.agent_type, [])

    async def process_update(self, data: Dict[str, Any]):
        """Process an update from another service."""
        try:
            # Process the update based on the source service
            result = await self.process(data)
            
            # Save artifacts
            self.save_artifacts(result)
            
            # Broadcast update to dependent services
            await self.communicator.broadcast_update({
                "source": self.agent_type,
                "type": "update",
                "data": result
            })
            
        except Exception as e:
            print(f"Error processing update: {str(e)}")
            await self.communicator.broadcast_update({
                "source": self.agent_type,
                "type": "error",
                "error": str(e)
            })

    async def start_service(self):
        """Start the service and its communication layer."""
        try:
            # Start the communicator
            await self.communicator.start()
            
            # Load initial state
            state = self.communicator.load_state()
            if state:
                print(f"Loaded state for {self.agent_type} service")
                
            print(f"\n{self.agent_type} service started and listening for updates")
            
            # Keep the service running
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            print(f"\n{self.agent_type} service shutting down...")
        except Exception as e:
            print(f"Error in {self.agent_type} service: {str(e)}")

    @abstractmethod
    async def process(self, input_data: Any) -> Dict[str, Any]:
        """Process input data and generate results."""
        pass

    def save_artifacts(self, result: Dict[str, Any]) -> None:
        """Save generated artifacts."""
        # Save the raw result
        result_file = self.get_artifact_path("result.json")
        with open(result_file, 'w') as f:
            json.dump(result, f, indent=2)
            
        # Save service state
        self.communicator.save_state({
            "last_update": datetime.now().isoformat(),
            "status": "completed",
            "result": result
        })

    def get_artifact_path(self, filename: str) -> Path:
        """Get the full path for an artifact file."""
        return self.output_dir / filename
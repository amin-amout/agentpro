"""Service communication module for inter-service messaging."""
import os
import json
import time
import asyncio
import aiohttp
import watchdog.events
import watchdog.observers
from pathlib import Path
from typing import Dict, Any, Callable, Optional
from aiohttp import web

class ServiceCommunicator:
    def __init__(self, service_name: str, project_name: str, port: int):
        self.service_name = service_name
        self.project_name = project_name
        self.port = port
        self.base_path = Path("projects") / project_name
        self.observers = {}
        self.app = web.Application()
        self.app.router.add_post("/notify", self.handle_notification)
        self.app.router.add_get("/status", self.handle_status)
        self.app.router.add_get("/artifacts", self.handle_artifacts)
        
        # Service discovery and configuration
        self.service_ports = {
            "architecture": 5001,
            "developer": 5002,
            "qa": 5003,
            "audit": 5004,
            "documentation": 5005
        }
        
        # Callbacks for different events
        self.callbacks = {
            "file_changed": [],
            "notification": []
        }

    async def start(self):
        """Start the REST API server and file watchers."""
        # Start watching other services' directories
        self._setup_watchers()
        
        # Start REST API server
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, "localhost", self.port)
        await site.start()
        print(f"{self.service_name} service listening on port {self.port}")

    def _setup_watchers(self):
        """Set up file system watchers for other services."""
        for service in self.service_ports.keys():
            if service != self.service_name:
                service_path = self.base_path / service
                if service_path.exists():
                    observer = watchdog.observers.Observer()
                    handler = ServiceFileHandler(
                        service_path,
                        self._handle_file_change
                    )
                    observer.schedule(handler, str(service_path), recursive=True)
                    observer.start()
                    self.observers[service] = observer

    def _handle_file_change(self, event):
        """Handle file change events from other services."""
        if event.src_path.endswith(".json"):
            try:
                with open(event.src_path) as f:
                    data = json.load(f)
                
                # Notify all registered callbacks
                for callback in self.callbacks["file_changed"]:
                    asyncio.create_task(callback(data))
            except Exception as e:
                print(f"Error processing file change: {str(e)}")

    async def notify_service(self, service: str, data: Dict[str, Any]):
        """Notify another service via REST API."""
        if service not in self.service_ports:
            print(f"Unknown service: {service}")
            return

        port = self.service_ports[service]
        url = f"http://localhost:{port}/notify"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data) as response:
                    return await response.json()
        except Exception as e:
            print(f"Error notifying service {service}: {str(e)}")

    async def broadcast_update(self, data: Dict[str, Any]):
        """Broadcast an update to all other services."""
        for service in self.service_ports.keys():
            if service != self.service_name:
                await self.notify_service(service, data)

    def on_file_changed(self, callback: Callable):
        """Register a callback for file change events."""
        self.callbacks["file_changed"].append(callback)

    def on_notification(self, callback: Callable):
        """Register a callback for REST API notifications."""
        self.callbacks["notification"].append(callback)

    async def handle_notification(self, request: web.Request):
        """Handle incoming REST API notifications."""
        data = await request.json()
        
        # Notify all registered callbacks
        for callback in self.callbacks["notification"]:
            asyncio.create_task(callback(data))
            
        return web.json_response({"status": "ok"})

    async def handle_status(self, request: web.Request):
        """Handle status check requests."""
        return web.json_response({
            "service": self.service_name,
            "status": "running",
            "project": self.project_name
        })

    async def handle_artifacts(self, request: web.Request):
        """Handle artifact list requests."""
        service_path = self.base_path / self.service_name
        artifacts = []
        
        if service_path.exists():
            for path in service_path.rglob("*"):
                if path.is_file():
                    artifacts.append(str(path.relative_to(service_path)))
                    
        return web.json_response({
            "service": self.service_name,
            "artifacts": artifacts
        })

    def save_state(self, state: Dict[str, Any]):
        """Save service state to a JSON file."""
        state_file = self.base_path / self.service_name / "state.json"
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def load_state(self) -> Optional[Dict[str, Any]]:
        """Load service state from JSON file."""
        state_file = self.base_path / self.service_name / "state.json"
        if state_file.exists():
            with open(state_file) as f:
                return json.load(f)
        return None

class ServiceFileHandler(watchdog.events.FileSystemEventHandler):
    def __init__(self, base_path: Path, callback: Callable):
        self.base_path = base_path
        self.callback = callback

    def on_modified(self, event):
        if event.is_directory:
            return
        self.callback(event)

    def on_created(self, event):
        if event.is_directory:
            return
        self.callback(event)
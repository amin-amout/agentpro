"""Service daemon runner for continuous operation."""
import os
import sys
import asyncio
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

from services.business_service import BusinessService
from services.architecture_service import ArchitectureService
from services.developer_service import DeveloperService
from services.qa_service import QAService
from services.audit_service import AuditService
from services.documentation_service import DocumentationService

# Map of service types to their classes
SERVICE_MAP = {
    "business": BusinessService,
    "architecture": ArchitectureService,
    "developer": DeveloperService,
    "qa": QAService,
    "audit": AuditService,
    "documentation": DocumentationService
}

async def run_service_daemon(service_type: str, project_name: str) -> None:
    """Run a service in daemon mode, listening for updates."""
    try:
        # Get the service class
        service_class = SERVICE_MAP.get(service_type)
        if not service_class:
            print(f"Error: Unknown service type '{service_type}'")
            return

        # Create and start the service
        print(f"\nStarting {service_type} service in daemon mode...")
        service = service_class(project_name)
        await service.start_service()
            
    except Exception as e:
        print(f"\nError running service: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    parser = argparse.ArgumentParser(description="Service Daemon Runner")
    parser.add_argument("--project-name", type=str, required=True, help="Name of the project")
    parser.add_argument("--service", type=str, required=True, choices=list(SERVICE_MAP.keys()),
                    help="Service to run (business, architecture, developer, qa, audit, documentation)")
    args = parser.parse_args()

    # Run the service daemon
    try:
        asyncio.run(run_service_daemon(args.service, args.project_name))
    except KeyboardInterrupt:
        print("\nService daemon stopped by user")
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
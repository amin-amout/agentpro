"""Documentation generation service."""
from pathlib import Path
from typing import Dict, Any
import json
from .base_service import BaseAgentService

class DocumentationService(BaseAgentService):
    @property
    def agent_type(self) -> str:
        return "documentation"

    async def process(self, input_data: str) -> Dict[str, Any]:
        """Generate project documentation."""
        messages = [
            {
                "role": "system",
                "content": """You are a Technical Writer specialized in software documentation.
                Create complete project documentation including:
                1. Project Overview
                2. Setup Guide
                3. User Guide
                4. API Documentation
                5. Development Guide
                6. Deployment Guide
                
                Format the output as structured JSON with markdown content."""
            },
            {
                "role": "user",
                "content": f"Create complete project documentation for: {input_data}"
            }
        ]
        
        response = self._call_llm_api(messages)
        content = response["choices"][0]["message"]["content"]
        
        try:
            result = json.loads(content)
        except json.JSONDecodeError:
            result = {"raw_content": content}
            
        return {
            "status": "success",
            "documentation": result
        }

    def save_artifacts(self, result: Dict[str, Any]) -> None:
        """Generate and save documentation files."""
        if result["status"] != "success":
            return

        # Save raw documentation data
        docs_path = self.get_artifact_path("documentation.json")
        with open(docs_path, 'w') as f:
            json.dump(result["documentation"], f, indent=2)

        docs = result["documentation"]
        
        # Create docs directory
        docs_dir = self.output_dir / "docs"
        docs_dir.mkdir(exist_ok=True)

        # Generate documentation files
        if "sections" in docs:
            for section in docs["sections"]:
                filename = f"{section['title'].lower().replace(' ', '_')}.md"
                file_path = docs_dir / filename
                with open(file_path, 'w') as f:
                    f.write(section["content"])

        # Generate mkdocs.yml for documentation site
        mkdocs_content = {
            "site_name": docs.get("project_name", "Project Documentation"),
            "theme": {
                "name": "material",
                "features": [
                    "navigation.tabs",
                    "navigation.sections",
                    "navigation.top",
                    "search.highlight"
                ]
            },
            "nav": [
                {"Home": "index.md"}
            ]
        }

        # Add documentation sections to navigation
        if "sections" in docs:
            for section in docs["sections"]:
                filename = f"{section['title'].lower().replace(' ', '_')}.md"
                mkdocs_content["nav"].append({
                    section["title"]: filename
                })

        mkdocs_path = self.get_artifact_path("mkdocs.yml")
        with open(mkdocs_path, 'w') as f:
            import yaml
            yaml.dump(mkdocs_content, f, sort_keys=False)

        # Generate main index.md
        index_content = [
            f"# {docs.get('project_name', 'Project Documentation')}\n",
            docs.get("project_description", ""),
            "\n## Documentation Sections\n"
        ]

        if "sections" in docs:
            for section in docs["sections"]:
                link = section["title"].lower().replace(" ", "_")
                index_content.append(f"- [{section['title']}]({link}.md)")

        index_path = docs_dir / "index.md"
        with open(index_path, 'w') as f:
            f.write("\n".join(index_content))

        # Generate README with setup instructions
        readme_content = [
            "# Project Documentation\n",
            docs.get("project_description", ""),
            "\n## Documentation Structure\n",
            "```",
            self._generate_tree_structure(docs_dir),
            "```\n",
            "## Building Documentation\n",
            "1. Install MkDocs Material theme:\n",
            "```bash",
            "pip install mkdocs-material",
            "```\n",
            "2. Build and serve documentation:\n",
            "```bash",
            "mkdocs serve  # For development",
            "mkdocs build  # For production",
            "```"
        ]

        readme_path = self.get_artifact_path("README.md")
        with open(readme_path, 'w') as f:
            f.write("\n".join(readme_content))

    def _generate_tree_structure(self, path: Path, prefix: str = "") -> str:
        """Generate a tree-like structure of the documentation files."""
        if not path.is_dir():
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
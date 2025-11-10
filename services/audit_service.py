"""Code audit service."""
from pathlib import Path
from typing import Dict, Any
import json
from .base_service import BaseAgentService

class AuditService(BaseAgentService):
    @property
    def agent_type(self) -> str:
        return "audit"

    async def process(self, input_data: str) -> Dict[str, Any]:
        """Review code quality and compliance."""
        messages = [
            {
                "role": "system",
                "content": """You are a Code Auditor specialized in code quality.
                Perform a comprehensive code audit including:
                1. Code Quality Analysis
                2. Security Review
                3. Performance Analysis
                4. Best Practices Review
                5. Compliance Check
                6. Improvement Recommendations
                
                Format the output as structured JSON."""
            },
            {
                "role": "user",
                "content": f"Perform a code audit and find improvements for: {input_data}"
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
            "audit_report": result
        }

    def save_artifacts(self, result: Dict[str, Any]) -> None:
        """Generate and save audit reports."""
        if result["status"] != "success":
            return

        # Save raw audit report
        report_path = self.get_artifact_path("audit_report.json")
        with open(report_path, 'w') as f:
            json.dump(result["audit_report"], f, indent=2)

        audit = result["audit_report"]
        
        # Generate markdown report
        docs = [
            "# Code Audit Report\n",
            "## Executive Summary\n",
        ]

        if "summary" in audit:
            docs.append(audit["summary"])
            docs.append("\n")

        # Code Quality
        if "code_quality" in audit:
            docs.append("## Code Quality Analysis\n")
            quality = audit["code_quality"]
            if "metrics" in quality:
                docs.append("### Metrics\n")
                for metric, value in quality["metrics"].items():
                    docs.append(f"- {metric}: {value}")
            if "issues" in quality:
                docs.append("\n### Issues Found\n")
                for issue in quality["issues"]:
                    docs.append(f"- **{issue['severity']}**: {issue['description']}")
                    if "recommendation" in issue:
                        docs.append(f"  - Recommendation: {issue['recommendation']}")
            docs.append("\n")

        # Security Review
        if "security" in audit:
            docs.append("## Security Review\n")
            for finding in audit["security"]:
                docs.append(f"### {finding['title']}\n")
                docs.append(f"- Risk Level: {finding['risk_level']}")
                docs.append(f"- Description: {finding['description']}")
                if "mitigation" in finding:
                    docs.append(f"- Mitigation: {finding['mitigation']}")
                docs.append("\n")

        # Performance Analysis
        if "performance" in audit:
            docs.append("## Performance Analysis\n")
            for analysis in audit["performance"]:
                docs.append(f"### {analysis['area']}\n")
                docs.append(analysis['findings'])
                if "recommendations" in analysis:
                    docs.append("\nRecommendations:")
                    for rec in analysis["recommendations"]:
                        docs.append(f"- {rec}")
                docs.append("\n")

        # Best Practices
        if "best_practices" in audit:
            docs.append("## Best Practices Review\n")
            for practice in audit["best_practices"]:
                docs.append(f"### {practice['category']}\n")
                docs.append(f"Status: {practice['status']}\n")
                if "violations" in practice:
                    docs.append("Violations:")
                    for violation in practice["violations"]:
                        docs.append(f"- {violation}")
                docs.append("\n")

        # Compliance
        if "compliance" in audit:
            docs.append("## Compliance Check\n")
            for check in audit["compliance"]:
                docs.append(f"### {check['standard']}\n")
                docs.append(f"Status: {check['status']}\n")
                if "findings" in check:
                    docs.append("Findings:")
                    for finding in check["findings"]:
                        docs.append(f"- {finding}")
                docs.append("\n")

        # Recommendations
        if "recommendations" in audit:
            docs.append("## Improvement Recommendations\n")
            for priority, recs in audit["recommendations"].items():
                docs.append(f"### {priority} Priority\n")
                for rec in recs:
                    docs.append(f"- {rec}\n")

        # Save markdown report
        report_md_path = self.get_artifact_path("audit_report.md")
        with open(report_md_path, 'w') as f:
            f.write("\n".join(docs))
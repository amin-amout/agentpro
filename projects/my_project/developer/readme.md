python -m orchestrator.main --agent developer

python service_runner.py --project-name my_project --service developer --input '{"architecture": '"$(cat projects/my_project/architecture/architecture.json)"', "specifications": '"$(cat projects/my_project/business/specifications.json)"'}'

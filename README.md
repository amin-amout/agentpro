# Multi-Agent Software Development System

This project implements a modular multi-agent system using Python and LangChain for collaborative software development. The system coordinates several specialized agents to design, develop, and audit software projects.

## System Architecture

The system consists of the following agents:

1. **Business Agent**: Gathers and defines requirements, interacts with humans for validation
2. **Architecture Agent**: Proposes system architecture and design patterns
3. **Developer Agent**: Writes implementation code modules
4. **QA Agent**: Generates test cases and validates correctness
5. **Audit Agent**: Reviews compliance, maintainability, and modularity
6. **Documentation Agent**: Produces human-readable documentation

Each agent operates independently but communicates through a shared message bus orchestrated by the main system.

## Project Structure

```
agentpro/
├── orchestrator/
│   ├── __init__.py
│   ├── config.py
│   ├── base_agent.py
│   ├── agents.py
│   ├── orchestrator.py
│   └── main.py
├── projects/
│   └── <project_name>/
│       ├── business/
│       ├── architecture/
│       ├── developer/
│       ├── qa/
│       ├── audit/
│       └── documentation/
├── requirements.txt
└── .env.example
```

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and configure your environment variables:
   ```bash
   cp .env.example .env
   ```
5. Edit `.env` with your API keys and preferences

## Usage

### Environment Setup

Before running any agents, ensure your `.env` file is configured with LLM credentials:

```bash
# .env example
LLM_API_KEY=your_groq_api_key_here
LLM_API_URL=https://api.groq.com/openai/v1/chat/completions
DEFAULT_MODEL=mixtral-8x7b-32768
TEMPERATURE=0.7
MAX_TOKENS=4096
```

Or use per-service config files:
```bash
# config/developer_config.json example
{
  "api_url": "https://api.groq.com/openai/v1/chat/completions",
  "api_key": "your_key_here",
  "model": "mixtral-8x7b-32768",
  "temperature": 0.7,
  "max_tokens": 4096
}
```

### Running the Full Workflow

```bash
python -m orchestrator.main --project-name my_project
```

This runs the complete pipeline: Business → Architecture → Developer → QA → Audit → Documentation.

---

## Agent Command Line Reference

### Method 1: Service Runner (Recommended for Individual Agents)

Use `service_runner.py` to run agents independently with full control over input and output.

#### General Syntax
```bash
python service_runner.py --project-name <name> --service <service> --input <input_data>
```

#### Parameters
- `--project-name` (required): Name of the project (creates/uses directory under `projects/`)
- `--service` (required): One of: `business`, `architecture`, `developer`, `qa`, `audit`, `documentation`
- `--input` (optional): Input data as JSON string or file path. If omitted, you'll be prompted interactively.

---

### 1. Business Agent
Gathers requirements, creates user stories, and generates functional/non-functional specifications.

#### Run with inline JSON input:
```bash
python service_runner.py \
  --project-name my_project \
  --service business \
  --input '{"title": "E-commerce Platform", "description": "Build a scalable online store with payment processing"}'
```

#### Run with file input:
```bash
python service_runner.py \
  --project-name my_project \
  --service business \
  --input requirements.json
```

#### Run interactively (prompts for input):
```bash
python service_runner.py \
  --project-name my_project \
  --service business
# Then enter your requirements at the prompt
```

**Output:**
- `projects/my_project/business/specifications.json` - Detailed project specifications
- `projects/my_project/business/requirements.md` - Human-readable requirements document

**Input Format (JSON):**
```json
{
  "title": "Project Name",
  "description": "Project description",
  "targetAudience": "Who will use this",
  "platforms": ["web", "mobile"],
  "deployment": "cloud/on-premise"
}
```

---

### 2. Architecture Agent
Designs system architecture, components, data models, and API specifications based on requirements.

#### Run after Business agent (using its output):
```bash
python service_runner.py \
  --project-name my_project \
  --service architecture \
  --input "$(cat projects/my_project/business/specifications.json)"
```

#### Run with direct file:
```bash
python service_runner.py \
  --project-name my_project \
  --service architecture \
  --input projects/my_project/business/specifications.json
```

#### Run with JSON string:
```bash
python service_runner.py \
  --project-name my_project \
  --service architecture \
  --input '{"specifications": {"name": "E-commerce", "type": "web-application"}}'
```

**Output:**
- `projects/my_project/architecture/architecture.json` - Complete system architecture specification
- Architecture diagrams in markdown format

**Input Format:** Specifications JSON from Business agent or custom architecture requirements

---

### 3. Developer Agent
Generates implementation code files based on architecture specifications.

#### Run after Architecture agent:
```bash
python service_runner.py \
  --project-name my_project \
  --service developer \
  --input "$(cat projects/my_project/architecture/architecture.json)"
```

#### Run with combined architecture + specifications:
```bash
python service_runner.py \
  --project-name my_project \
  --service developer \
  --input projects/my_project/developer_input.json
```

#### Specify custom project path (creates fresh output):
```bash
python service_runner.py \
  --project-name another_project \
  --service developer \
  --input "$(cat projects/my_project/architecture/architecture.json)"
```

**Output:**
- `projects/my_project/developer/index.html` - Entry HTML file
- `projects/my_project/developer/main.js` - Main JavaScript entry
- `projects/my_project/developer/styles.css` - CSS styling
- `projects/my_project/developer/src/*.js` - Individual module implementations

**Input Format:** Architecture JSON with module specifications

---

### 4. QA Agent
Creates comprehensive test plans, test cases, and validation strategies.

#### Run after Developer agent:
```bash
python service_runner.py \
  --project-name my_project \
  --service qa \
  --input "$(cat projects/my_project/developer/result.json)"
```

#### Run with implementation details:
```bash
python service_runner.py \
  --project-name my_project \
  --service qa \
  --input '{"implementation": {"modules": ["auth", "payment", "cart"]}}'
```

**Output:**
- `projects/my_project/qa/test_plan.json` - Comprehensive test plan
- `projects/my_project/qa/tests/test_unit.py` - Unit tests
- `projects/my_project/qa/tests/test_integration.py` - Integration tests
- `projects/my_project/qa/tests/test_performance.py` - Performance tests
- `projects/my_project/qa/test_documentation.md` - Test documentation

**Input Format:** Implementation details, module descriptions, or developer output JSON

---

### 5. Audit Agent
Performs code quality review, security analysis, and compliance checks.

#### Run on implementation code:
```bash
python service_runner.py \
  --project-name my_project \
  --service audit \
  --input "$(cat projects/my_project/developer/main.js)"
```

#### Run with file content:
```bash
python service_runner.py \
  --project-name my_project \
  --service audit \
  --input projects/my_project/developer/src/gameEngine.js
```

**Output:**
- `projects/my_project/audit/audit_report.json` - Comprehensive audit findings
- `projects/my_project/audit/audit_report.md` - Formatted audit report with:
  - Code quality metrics
  - Security vulnerabilities
  - Performance issues
  - Best practices violations
  - Compliance findings
  - Improvement recommendations

**Input Format:** Source code (single file or JSON with code content)

---

### 6. Documentation Agent
Generates project documentation, guides, API docs, and deployment instructions.

#### Run on complete project:
```bash
python service_runner.py \
  --project-name my_project \
  --service documentation \
  --input "$(cat projects/my_project/architecture/architecture.json)"
```

#### Generate docs with specifications:
```bash
python service_runner.py \
  --project-name my_project \
  --service documentation \
  --input projects/my_project/business/specifications.json
```

**Output:**
- `projects/my_project/documentation/documentation.json` - Structured documentation
- `projects/my_project/documentation/docs/` - Markdown documentation files:
  - `project_overview.md`
  - `setup_guide.md`
  - `user_guide.md`
  - `api_documentation.md`
  - `development_guide.md`
  - `deployment_guide.md`
- `projects/my_project/documentation/mkdocs.yml` - MkDocs configuration
- `projects/my_project/documentation/README.md` - Documentation index

**Input Format:** Architecture JSON, specifications JSON, or project description

---

### Method 2: Orchestrator (Full Workflow)

Use the orchestrator for complete end-to-end automation.

#### Run full pipeline interactively:
```bash
python -m orchestrator.main --project-name my_project
```
Prompts for project requirements, then runs all agents in sequence.

#### Run specific agent via orchestrator:
```bash
python -m orchestrator.main --project-name my_project --agent business
```

#### Available agents via orchestrator:
- `business` - Requirement gathering
- `architecture` - System design
- `developer` - Code generation
- `qa` - Test generation
- `audit` - Code review
- `documentation` - Doc generation

---

## Complete Workflow Examples

### Example 1: End-to-End Project Generation

```bash
# Step 1: Gather business requirements
python service_runner.py \
  --project-name ecommerce \
  --service business \
  --input '{"title": "Online Store", "description": "E-commerce platform with product catalog and checkout"}'

# Step 2: Design architecture
python service_runner.py \
  --project-name ecommerce \
  --service architecture \
  --input "$(cat projects/ecommerce/business/specifications.json)"

# Step 3: Generate implementation code
python service_runner.py \
  --project-name ecommerce \
  --service developer \
  --input "$(cat projects/ecommerce/architecture/architecture.json)"

# Step 4: Create test plan
python service_runner.py \
  --project-name ecommerce \
  --service qa \
  --input "$(cat projects/ecommerce/developer/result.json)"

# Step 5: Audit code quality
python service_runner.py \
  --project-name ecommerce \
  --service audit \
  --input "$(cat projects/ecommerce/developer/main.js)"

# Step 6: Generate documentation
python service_runner.py \
  --project-name ecommerce \
  --service documentation \
  --input "$(cat projects/ecommerce/business/specifications.json)"
```

### Example 2: Update Specific Component

```bash
# Update architecture only
python service_runner.py \
  --project-name ecommerce \
  --service architecture \
  --input "$(cat projects/ecommerce/business/specifications.json)"

# Regenerate code based on new architecture
python service_runner.py \
  --project-name ecommerce \
  --service developer \
  --input "$(cat projects/ecommerce/architecture/architecture.json)"
```

---

## Project State Management

Each project maintains state in `projects/<project_name>/project_state.json`:

```json
{
  "business": {
    "status": "completed",
    "timestamp": "2025-11-10T12:00:00",
    "artifacts": ["specifications.json", "requirements.md"]
  },
  "architecture": {
    "status": "completed",
    "timestamp": "2025-11-10T12:15:00",
    "artifacts": ["architecture.json"]
  }
}
```

View current project state:
```bash
cat projects/my_project/project_state.json | python -m json.tool
```

---

## Output Directory Structure

After running all agents:
```
projects/my_project/
├── business/
│   ├── specifications.json
│   └── requirements.md
├── architecture/
│   └── architecture.json
├── developer/
│   ├── index.html
│   ├── main.js
│   ├── styles.css
│   └── src/
│       ├── gameEngine.js
│       ├── physicsEngine.js
│       └── ...
├── qa/
│   ├── test_plan.json
│   └── tests/
│       ├── test_unit.py
│       ├── test_integration.py
│       └── test_performance.py
├── audit/
│   ├── audit_report.json
│   └── audit_report.md
├── documentation/
│   ├── documentation.json
│   ├── docs/
│   │   ├── setup_guide.md
│   │   ├── api_documentation.md
│   │   └── ...
│   └── mkdocs.yml
└── project_state.json
```

## LLM Configuration

The system supports both Groq and local LLM endpoints:

- **Groq API**: Set `LLM_API_TYPE=groq` in `.env`
- **Local LLM**: Set `LLM_API_TYPE=local` and configure `LOCAL_LLM_URL` in `.env`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License
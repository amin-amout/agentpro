"""LangChain components for agent coordination."""
from typing import Dict, Any, List
from langchain_core.tools import Tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.language_models import BaseChatModel

from .llm import GroqLLM
from .agents import (
    BusinessAgent,
    ArchitectureAgent,
    DeveloperAgent,
    QAAgent,
    AuditAgent,
    DocumentationAgent
)

class AgentCoordinator:
    def __init__(self, llm_config: Dict[str, Any]):
        self.llm_config = llm_config
        
        # Initialize LLM
        self.llm = GroqLLM(
            api_url=llm_config["api_url"],
            api_key=llm_config["api_key"],
            model=llm_config["model"]
        )
        
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Initialize domain-specific agents
        self.business_agent = BusinessAgent(llm_config)
        self.architecture_agent = ArchitectureAgent(llm_config)
        self.developer_agent = DeveloperAgent(llm_config)
        self.qa_agent = QAAgent(llm_config)
        self.audit_agent = AuditAgent(llm_config)
        self.doc_agent = DocumentationAgent(llm_config)
        
        # Create tools for each agent
        self.tools = [
            Tool(
                name="BusinessAnalysis",
                func=self.business_agent.process,
                description="Analyze project requirements and create detailed specifications",
                return_direct=True
            ),
            Tool(
                name="ArchitectureDesign",
                func=self.architecture_agent.process,
                description="Design a complete system architecture based on requirements",
                return_direct=True
            ),
            Tool(
                name="Implementation",
                func=self.developer_agent.process,
                description="Write code implementations based on architecture or specifications",
                return_direct=True
            ),
            Tool(
                name="QualityAssurance",
                func=self.qa_agent.process,
                description="Create test plans and test cases for implementations",
                return_direct=True
            ),
            Tool(
                name="CodeAudit",
                func=self.audit_agent.process,
                description="Review code quality and find improvements",
                return_direct=True
            ),
            Tool(
                name="Documentation",
                func=self.doc_agent.process,
                description="Generate complete project documentation",
                return_direct=True
            )
        ]

    async def run_workflow(self, initial_prompt: str) -> Dict[str, Any]:
        """Run the complete agent workflow using LangChain coordination."""
        try:
            # Create the prompt template
            # Load coordinator system prompt from shared prompts
            prompt_path = Path(__file__).parent.parent / 'services' / 'prompts' / 'coordinator.txt'
            if not prompt_path.exists():
                raise FileNotFoundError(f"Missing coordinator prompt: {prompt_path}")
            coordinator_prompt = prompt_path.read_text()

            template = ChatPromptTemplate.from_messages([
                ("system", coordinator_prompt),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])

            # Create the agent
            agent = create_openai_functions_agent(
                llm=self.llm,
                tools=self.tools,
                prompt=template
            )

            # Create a simple executor
            agent_executor = AgentExecutor.from_agent_and_tools(
                agent=agent,
                tools=self.tools,
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=3
            )

            # Run the workflow
            result = await agent_executor.ainvoke({
                "input": f"Create a detailed plan for this project: {initial_prompt}"
            })
            
            # Extract the workflow result
            output = result.get("output", "")
            workflow_result = str(output) if output else "No output generated"

            return {
                "status": "success",
                "workflow_result": workflow_result
            }

        except Exception as e:
            print(f"\nDetailed error: {str(e)}")
            if hasattr(e, "__cause__") and e.__cause__:
                print(f"Caused by: {str(e.__cause__)}")
            return {
                "status": "error",
                "error": str(e)
            }
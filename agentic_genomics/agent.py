import asyncio
from adk.agent import Agent
from adk.coder import Skill
from adk.llm import LLMProvider, DefaultLLMProvider
from agentic_genomics.tools.deployment_workflow import DeploymentWorkflow # Will be created in next step
from typing import Dict, Any

class OrchestratorAgent(Agent):
    def __init__(self, llm_provider: LLMProvider = None, **kwargs):
        actual_llm_provider = llm_provider or DefaultLLMProvider()
        # Provide a default agent_name if not given, as it's often expected by Agent's __init__
        agent_name = kwargs.pop('agent_name', self.__class__.__name__)
        super().__init__(llm_provider=actual_llm_provider, agent_name=agent_name, **kwargs)
        print(f"OrchestratorAgent '{self.agent_name}' initialized.")

    @Skill(
        name="run_genomics_deployment_workflow",
        description="Initiates and manages the Nextflow deployment workflow, from discovery to execution.",
        parameters={"user_query": {"type": "string", "description": "User's request or parameters for the deployment."}},
        output_type={"workflow_result": {"type": "object"}}
    )
    async def run_genomics_deployment_workflow(self, user_query: str) -> Dict[str, Any]:
        print(f"OrchestratorAgent '{self.agent_name}': Received query '{user_query}'. Initiating DeploymentWorkflow.")

        # Pass the llm_provider to the workflow.
        # The workflow itself might need an LLM, or its constituent agents might.
        workflow = DeploymentWorkflow(llm_provider=self.llm_provider)

        print(f"OrchestratorAgent '{self.agent_name}': DeploymentWorkflow instantiated. Starting workflow run...")
        initial_workflow_input = {"query": user_query, "details": "Initial input for pipeline discovery"}

        try:
            # ADK's SequentialAgent.run is synchronous.
            if hasattr(asyncio, 'to_thread'):
                workflow_result = await asyncio.to_thread(workflow.run, initial_workflow_input)
            else:
                loop = asyncio.get_event_loop()
                workflow_result = await loop.run_in_executor(None, workflow.run, initial_workflow_input)

            print(f"OrchestratorAgent '{self.agent_name}': DeploymentWorkflow finished. Result: {workflow_result}")
            return {"status": "success", "message": "Workflow completed.", "workflow_output": workflow_result}
        except Exception as e:
            print(f"OrchestratorAgent '{self.agent_name}': Error during workflow execution: {e}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "message": str(e), "workflow_output": None}

    async def aask(self, query: str, context: str = "") -> str:
        # This is the primary entry point if using OrchestratorAgent like a standard agent.
        print(f"OrchestratorAgent '{self.agent_name}' aask called with query: {query}")
        result = await self.run_genomics_deployment_workflow(user_query=query)
        # Ensure the final response is a string as expected by aask
        import json
        return json.dumps(result)

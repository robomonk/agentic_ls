from adk.agent import Agent
from adk.coder import Skill
from adk.llm import LLMProvider
from agentic_genomics.tools import NextflowConfigTool # Corrected import path
from typing import Dict, Any

class BlueprintArchitectAgent(Agent):
    def __init__(self, llm_provider: LLMProvider = None, **kwargs):
        super().__init__(llm_provider=llm_provider, **kwargs)
        self.nextflow_config_tool = NextflowConfigTool()
        self.register_tool(self.nextflow_config_tool)
        print(f"BlueprintArchitectAgent initialized and registered {self.nextflow_config_tool.name} tool.")

    @Skill(
        name="generate_deployment_blueprint",
        description="Generates the Nextflow configuration files (blueprint) based on the configured pipeline details.",
        # parameters={"configured_pipeline_data": {"type": "object", "description": "Data from the ConfiguratorAgent."}},
        # output_type={"blueprint_files": {"type": "array", "items": {"type": "string"}}}
    )
    async def generate_deployment_blueprint(self, configured_pipeline_data: Dict[str, Any]) -> Dict[str, Any]:
        print(f"BlueprintArchitectAgent: Received configured data: {configured_pipeline_data}. Executing generate_deployment_blueprint skill.")

        # Placeholder logic: pass the received data to the tool
        tool_result = self.nextflow_config_tool.run(pipeline_details=configured_pipeline_data)
        print(f"BlueprintArchitectAgent: Tool {self.nextflow_config_tool.name} executed, result: {tool_result}")

        return {"status": "success", "message": "Deployment blueprint generated (placeholder).", "data": tool_result}

    async def aask(self, query: str, context: str = "") -> str:
        print(f"BlueprintArchitectAgent aask called with query: {query}. Returning placeholder response.")
        # Mock input based on expected data from ConfiguratorAgent
        mock_configured_data = {"pipeline_id": "placeholder_pipeline", "config_status": "configured_placeholder"}
        result = await self.generate_deployment_blueprint(configured_pipeline_data=mock_configured_data)
        return f"BlueprintArchitectAgent placeholder response: {result}"

    def process_run_output(self, run_output: Dict[str, Any]) -> Dict[str, Any]:
        """Processes the output from the agent's run method for sequential execution."""
        print(f"BlueprintArchitectAgent: Processing run output: {run_output}")
        if run_output and run_output.get("data"):
            return run_output["data"] # Pass the tool's direct output
        return {"error": "No data from BlueprintArchitectAgent skill."}

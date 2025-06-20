from adk.agent import Agent
from adk.coder import Skill
from adk.llm import LLMProvider
from agentic_genomics.tools import PipelineConfigTool # Corrected import path
from typing import Dict, Any, List

class ConfiguratorAgent(Agent):
    def __init__(self, llm_provider: LLMProvider = None, **kwargs):
        super().__init__(llm_provider=llm_provider, **kwargs)
        self.pipeline_config_tool = PipelineConfigTool()
        self.register_tool(self.pipeline_config_tool)
        print(f"ConfiguratorAgent initialized and registered {self.pipeline_config_tool.name} tool.")

    @Skill(
        name="configure_selected_pipeline",
        description="Configures the selected Nextflow pipeline based on available options and user inputs.",
        # parameters={"pipeline_id": {"type": "string", "description": "The ID of the pipeline to configure."},
        #             "user_preferences": {"type": "object", "description": "User's configuration preferences."}},
        # output_type={"configuration_details": {"type": "object"}}
    )
    async def configure_selected_pipeline(self, discovered_pipelines: List[Dict[str, Any]], user_preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        print(f"ConfiguratorAgent: Received discovered pipelines: {discovered_pipelines}, user_preferences: {user_preferences}. Executing configure_selected_pipeline skill.")

        # Placeholder logic: pick the first discovered pipeline if available
        pipeline_to_configure = "unknown_pipeline"
        if discovered_pipelines and isinstance(discovered_pipelines, list) and discovered_pipelines[0]:
            # Assuming the tool output from scout was like: {"discovered_pipelines": ["pipeline_A_v1.nf", ...]}
            if isinstance(discovered_pipelines[0], str): # Check if it's a list of strings
                 pipeline_to_configure = discovered_pipelines[0]
            elif isinstance(discovered_pipelines[0], dict) and "name" in discovered_pipelines[0]: # Or list of dicts
                 pipeline_to_configure = discovered_pipelines[0]["name"]


        print(f"ConfiguratorAgent: Attempting to configure pipeline: {pipeline_to_configure}")
        tool_result = self.pipeline_config_tool.run(pipeline_id=pipeline_to_configure)
        print(f"ConfiguratorAgent: Tool {self.pipeline_config_tool.name} executed, result: {tool_result}")

        return {"status": "success", "message": f"Pipeline {pipeline_to_configure} configured (placeholder).", "data": tool_result}

    async def aask(self, query: str, context: str = "") -> str:
        print(f"ConfiguratorAgent aask called with query: {query}. Returning placeholder response.")
        # This might be more complex depending on how context (previous agent's output) is passed
        # For now, we'll assume the context might contain the pipeline_id or relevant info.
        # In a SequentialWorkflow, the input to this agent's skill will be managed by the workflow.
        discovered_data = {"discovered_pipelines": ["placeholder_from_aask_context.nf"]} # Mock input
        result = await self.configure_selected_pipeline(discovered_pipelines=discovered_data.get("discovered_pipelines", []))
        return f"ConfiguratorAgent placeholder response: {result}"

    def process_run_output(self, run_output: Dict[str, Any]) -> Dict[str, Any]:
        """Processes the output from the agent's run method for sequential execution."""
        print(f"ConfiguratorAgent: Processing run output: {run_output}")
        if run_output and run_output.get("data"):
            return run_output["data"] # Pass the tool's direct output
        return {"error": "No data from ConfiguratorAgent skill."}

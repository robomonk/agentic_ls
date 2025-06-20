from adk.agent import Agent
from adk.coder import Skill
from adk.llm import LLMProvider
from agentic_genomics.tools import PipelineDiscoveryTool # Corrected import path
from typing import Dict, Any

class PipelineScoutAgent(Agent):
    def __init__(self, llm_provider: LLMProvider = None, **kwargs):
        super().__init__(llm_provider=llm_provider, **kwargs)
        self.pipeline_discovery_tool = PipelineDiscoveryTool()
        self.register_tool(self.pipeline_discovery_tool)
        print(f"PipelineScoutAgent initialized and registered {self.pipeline_discovery_tool.name} tool.")

    @Skill(
        name="discover_available_pipelines",
        description="Discovers available Nextflow pipelines based on user query or predefined criteria.",
        # parameters={"query": {"type": "string", "description": "User query for pipeline discovery."}},
        # output_type={"discovered_pipelines": {"type": "array", "items": {"type": "object"}}}
    )
    async def discover_available_pipelines(self, query: str = "") -> Dict[str, Any]:
        print(f"PipelineScoutAgent: Received query '{query}', executing discover_available_pipelines skill.")
        # In a real agent, the query might be processed or passed to the tool
        tool_result = self.pipeline_discovery_tool.run() # No specific args for placeholder
        print(f"PipelineScoutAgent: Tool {self.pipeline_discovery_tool.name} executed, result: {tool_result}")
        return {"status": "success", "message": "Pipelines discovered (placeholder).", "data": tool_result}

    # Required by ADK, even if not used in SequentialAgent context directly for this iteration
    async def aask(self, query: str, context: str = "") -> str:
        print(f"PipelineScoutAgent aask called with query: {query}. Returning placeholder response.")
        # For sequential execution, the primary skill is usually called directly by the workflow.
        # This aask might be used if the agent is invoked in a different way.
        result = await self.discover_available_pipelines(query=query)
        return f"PipelineScoutAgent placeholder response: {result}"

    def process_run_output(self, run_output: Dict[str, Any]) -> Dict[str, Any]:
        """Processes the output from the agent's run method for sequential execution."""
        print(f"PipelineScoutAgent: Processing run output: {run_output}")
        # For this iteration, the output from the skill is directly usable.
        # This method is crucial in SequentialAgent for transforming/passing data.
        if run_output and run_output.get("data"):
            return run_output["data"] # Pass the tool's direct output
        return {"error": "No data from PipelineScoutAgent skill."}

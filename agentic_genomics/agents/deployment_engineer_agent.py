from adk.agent import Agent
from adk.coder import Skill
from adk.llm import LLMProvider
from agentic_genomics.tools import ExecutionTool # Corrected import path
from typing import Dict, Any, List

class DeploymentEngineerAgent(Agent):
    def __init__(self, llm_provider: LLMProvider = None, **kwargs):
        super().__init__(llm_provider=llm_provider, **kwargs)
        self.execution_tool = ExecutionTool()
        self.register_tool(self.execution_tool)
        print(f"DeploymentEngineerAgent initialized and registered {self.execution_tool.name} tool.")

    @Skill(
        name="deploy_and_execute_pipeline",
        description="Deploys and executes the Nextflow pipeline using the generated blueprint and configuration.",
        # parameters={"blueprint_data": {"type": "object", "description": "Data from the BlueprintArchitectAgent, including paths to config files."}},
        # output_type={"execution_status": {"type": "object"}}
    )
    async def deploy_and_execute_pipeline(self, blueprint_data: Dict[str, Any]) -> Dict[str, Any]:
        print(f"DeploymentEngineerAgent: Received blueprint data: {blueprint_data}. Executing deploy_and_execute_pipeline skill.")

        # Placeholder logic: construct a Nextflow command
        # Assuming blueprint_data might look like: {"blueprint_status": "generated_placeholder", "files": ["nextflow.config", "params.json"]}
        # And the actual pipeline script name might come from earlier stages or be fixed for now.
        pipeline_script = "main.nf" # Placeholder
        config_files_str = ""
        if blueprint_data and "files" in blueprint_data and isinstance(blueprint_data["files"], list):
            for f in blueprint_data["files"]:
                if "nextflow.config" in f: # Simple check
                    config_files_str += f" -c {f}" # This assumes files are in current dir or accessible path
                # Add params file if needed: else if "params.json" in f: config_files_str += f" --params_file {f}"

        nextflow_command = f"nextflow run {pipeline_script}{config_files_str} -profile docker --outdir ./results" # Basic command

        tool_result = self.execution_tool.run(nextflow_command=nextflow_command)
        print(f"DeploymentEngineerAgent: Tool {self.execution_tool.name} executed, result: {tool_result}")

        return {"status": "success", "message": "Pipeline execution initiated (placeholder).", "data": tool_result}

    async def aask(self, query: str, context: str = "") -> str:
        print(f"DeploymentEngineerAgent aask called with query: {query}. Returning placeholder response.")
        # Mock input
        mock_blueprint_data = {"blueprint_status": "generated_placeholder", "files": ["nextflow.config", "params.json"]}
        result = await self.deploy_and_execute_pipeline(blueprint_data=mock_blueprint_data)
        return f"DeploymentEngineerAgent placeholder response: {result}"

    def process_run_output(self, run_output: Dict[str, Any]) -> Dict[str, Any]:
        """Processes the output from the agent's run method for sequential execution."""
        print(f"DeploymentEngineerAgent: Processing run output: {run_output}")
        # The final output of the workflow.
        if run_output and run_output.get("data"):
            return run_output["data"]
        return {"error": "No data from DeploymentEngineerAgent skill."}

from google.adk.agents import LlmAgent, SequentialAgent
import tempfile
from google.adk.tools import BaseTool, tool_from_agent

# Import the specialized agents that will form the steps of the workflow.
from agents.pipeline_scout import PipelineScoutAgent
from agents.configurator import ConfiguratorAgent
from agents.blueprint_architect import BlueprintArchitectAgent
from agents.deployment_engineer import DeploymentEngineerAgent

class DeploymentWorkflowTool(BaseTool):
    """
    A tool that executes the full, sequential workflow for deploying a
    bioinformatics pipeline, orchestrating multiple specialist agents.
    """
    def __init__(self):
        # The core of this tool is a SequentialAgent that runs sub-agents in order,
        # passing the output of one as the input to the next.
        self._workflow_agent = SequentialAgent(
            sub_agents=[
                PipelineScoutAgent,
                ConfiguratorAgent,
                BlueprintArchitectAgent,
                DeploymentEngineerAgent,
            ]
        )
        # We wrap the SequentialAgent in a tool so the OrchestratorAgent can call it.
        self._tool = tool_from_agent(
            name="run_deployment_workflow",
            description="Initiates and runs the full pipeline deployment workflow, from selection to cloud deployment.",
            agent=self._workflow_agent
        )

    def _get_declaration(self):
        return self._tool.get_declaration()

    def _run(self, **kwargs):
        # Create a unique, secure temporary directory for this specific workflow run.
        with tempfile.TemporaryDirectory(prefix="agentic_genomics_") as temp_dir:
            # Prepend the working directory path to the user's request.
            # This makes all sub-agents aware of the unique path they should use for file I/O.
            original_request = kwargs.get("request", "")
            prefix = f"You are part of a workflow operating in the following secure temporary directory: '{temp_dir}'. All file outputs must be written to this directory.\n\nUser request: "
            kwargs["request"] = prefix + original_request

            return self._tool.run(**kwargs)
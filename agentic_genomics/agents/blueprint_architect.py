from google.adk.agents import LlmAgent
from google.adk.tools import get_user_choice
from tools.terraform_tools import CreateClusterToolkitBlueprintTool


BlueprintArchitectAgent = LlmAgent(
    name="blueprint_architect_agent",
    model='gemini-2.5-pro-preview-05-06',
    description="Generates a Terraform blueprint for provisioning a GCP cluster for Nextflow.",
    instruction="""
    You are a specialist agent that designs cloud infrastructure for running a Nextflow pipeline on Google Cloud Platform (GCP) using the official Google Cloud Cluster Toolkit.
    Your input will be the configuration details and resource requirements from the previous agent.

    Your workflow is as follows:
    1.  Analyze the input to determine the appropriate parameters for the Google Cloud Cluster Toolkit. This includes mapping high-level requirements (e.g., 'small compute cluster') to specific toolkit variables like `project_id`, `location`, `cluster_name`, machine types, etc.
    2.  Propose the infrastructure plan to the user, summarizing the key Cluster Toolkit parameters you've chosen. Ask for approval using the `get_user_choice` tool.
    3.  Upon approval, call the `create_cluster_toolkit_blueprint` tool. You must provide two arguments:
        - `blueprint_path`: A temporary path for the new blueprint, for example `/tmp/gcp_cluster_toolkit_blueprint`.
        - `toolkit_variables`: A dictionary containing the parameters you determined in step 1. Make sure that it contains values for `project_id`, `location`, and `cluster_name`. You must also include the `blueprint_path` in this dictionary.
    4.  Your final output must be a JSON object containing the path to the generated Terraform blueprint directory, which you will get from the tool's output.
        - Example: {"blueprint_path": "/tmp/gcp_cluster_toolkit_blueprint"}
        A resource summary is not necessary for this step, since the cost estimation will be performed in a future step, and can be inferred from the blueprint.
    """,
    tools=[
        get_user_choice,
        CreateClusterToolkitBlueprintTool(),
    ],
)
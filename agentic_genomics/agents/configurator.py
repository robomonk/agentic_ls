from google.adk.agents import LlmAgent
from google.adk.tools import get_user_choice
from tools.nextflow_tools import CreateNextflowConfigTool, CreateParamsJsonTool

ConfiguratorAgent = LlmAgent(
    name="configurator_agent",
    model='gemini-2.5-pro-preview-05-06',
    description="Configures a Nextflow pipeline with user-provided parameters.",
    instruction="""
    You are a specialist agent that configures a Nextflow pipeline for a specific run.
    Your input will be the name and schema of a pipeline selected by the PipelineScoutAgent.
    
    Your workflow is as follows:
    1.  Analyze the pipeline schema to identify mandatory parameters that the user must provide (e.g., input file paths, output directory).
    2.  Interact with the user to collect values for these mandatory parameters.
    3.  You must also ask the user for Google Cloud configuration details: the GCP Project ID, the region (e.g., 'us-central1'), and a GCS bucket path for the `workDir` (e.g., 'gs://my-bucket/work').
    4.  Once you have all parameters, use the `get_user_choice` tool to present a summary of the configuration to the user for final approval.
    5.  After approval, call the `create_params_json` tool with the user-provided pipeline parameters:
        - For the `params_data` parameter, provide a dictionary with keys `path` for the full path to `params.json` (using the temporary directory) and `content` for the dictionary of pipeline parameters.
    6.   Call the `create_nextflow_config` tool with the generated configuration content:
        - For the `config_content` parameter, construct a string with the full path to `nextflow.config` (inside the temporary directory) and the nextflow configuration using the user's cloud details.
        - Example: "/tmp/workflow-123/nextflow.config: profiles { standard { process.executor = 'google-batch'\ngoogle.project = 'my-gcp-project'\ngoogle.region  = 'us-central1'\nworkDir = 'gs://my-bucket/work'\ndocker.enabled = true }}"
    6.  Next, you must construct the content for a `nextflow.config` file that is configured for execution on Google Cloud Batch. This content MUST specify `process.executor = 'google-batch'`, the `workDir`, `google.project`, and `google.region`. It should also enable Docker.
    7.  Call the `create_nextflow_config` tool with the generated configuration content.
    8.  Your final output must be a JSON object containing the path to the generated `nextflow.config` in the key `nextflow_config_path` and to the `params.json` in the key `params_json_path`.
    """,
    tools=[
        get_user_choice,
        CreateNextflowConfigTool(),
        CreateParamsJsonTool(),
    ],
)

from google.adk.agents import LlmAgent
from google.adk.tools import get_user_choice
from tools.terraform_tools import ExecuteTerraformApplyTool

DeploymentEngineerAgent = LlmAgent(
    name="deployment_engineer_agent",
    model='gemini-2.5-pro-preview-05-06',
    description="Executes a Terraform blueprint to provision a GCP cluster.",
    instruction="""
    You are a specialist agent that deploys cloud infrastructure using Terraform.
    Your input will be the path to a directory containing a Terraform blueprint.

    Your workflow is as follows:
    1.  Acknowledge the blueprint path you have received.
    2.  This is the final step before incurring cloud costs. You MUST confirm with the user that they are ready to deploy the infrastructure. Use the `get_user_choice` tool for this critical final confirmation.
    3.  Upon user approval, use the `execute_terraform_apply` tool with the provided `blueprint_path` to provision the resources on GCP.
    4.  Your final output must be the result from the `execute_terraform_apply` tool, which includes the deployment status and any relevant cluster connection details.
    """,
    tools=[
        get_user_choice,
        ExecuteTerraformApplyTool(),
    ],
)

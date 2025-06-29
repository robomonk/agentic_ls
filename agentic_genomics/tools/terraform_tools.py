import json
import subprocess
from datetime import datetime
from pathlib import Path

from google.adk.tools import BaseTool, tool_code


class CreateClusterToolkitBlueprintTool(BaseTool):
    """
    A tool to generate a Terraform blueprint compatible with the Google Cloud Cluster Toolkit.
    """

    def _get_declaration(self):
        return tool_code(
            name="create_cluster_toolkit_blueprint",
            description="Generates a Terraform blueprint directory using the Google Cloud Cluster Toolkit module, configured with a .tfvars file.",
            parameters={
                "blueprint_path": {
                    "type": "string",
                    "description": "The absolute path where the blueprint directory will be created, e.g., '/tmp/gcp_blueprint'.",
                },
                "toolkit_variables": {
                    "type": "object",
                    "description": "A dictionary of variables to write into the terraform.tfvars file. Keys are variable names, values are their values.",
                },
            },
        )

    def _run(self, blueprint_path: str, toolkit_variables: dict) -> str:
        """Creates a main.tf and terraform.tfvars file in the specified directory."""
        try:
            bp_path = Path(blueprint_path)
            bp_path.mkdir(parents=True, exist_ok=True)

            # Create a main.tf that uses a GKE module from the cluster toolkit as an example.
            # A more advanced version could select different modules based on input.
            main_tf_content = """
module "gke_cluster" {
  # This example uses the GKE module. Other modules like 'gce' could also be used.
  source  = "GoogleCloudPlatform/cluster-toolkit/google//modules/gke"
  version = "2.0.0" # Pin to a specific version for stability

  project_id = var.project_id
  location   = var.location
  name       = var.cluster_name
}

variable "project_id" {
  type        = string
  description = "The GCP project ID."
}

variable "location" {
  type        = string
  description = "The GCP location (region or zone)."
}

variable "cluster_name" {
  type        = string
  description = "The name of the GKE cluster."
}
"""
            (bp_path / "main.tf").write_text(main_tf_content.strip())

            # Create terraform.tfvars from the dictionary
            tfvars_lines = [f"# Auto-generated by agentic_genomics on {datetime.now().isoformat()}"]
            for key, value in toolkit_variables.items():
                if isinstance(value, str):
                    escaped_value = value.replace("\\", "\\\\").replace('"', '\\"')
                    tfvars_lines.append(f'{key} = "{escaped_value}"')
                elif isinstance(value, bool):
                    tfvars_lines.append(f'{key} = {str(value).lower()}')
                elif isinstance(value, (int, float)):
                    tfvars_lines.append(f'{key} = {value}')
                else:
                    tfvars_lines.append(f"{key} = {json.dumps(value)}")

            (bp_path / "terraform.tfvars").write_text("\n".join(tfvars_lines))

            return f"Successfully created Cluster Toolkit blueprint at {blueprint_path}"
        except Exception as e:
            return f"Error creating blueprint: {e}"


class ExecuteTerraformApplyTool(BaseTool):
    """
    A tool to execute 'terraform init' and 'terraform apply'.
    """

    def _get_declaration(self):
        return tool_code(
            name="execute_terraform_apply",
            description="Runs 'terraform init' and 'terraform apply' in a specified directory.",
            parameters={"blueprint_path": {"type": "string", "description": "The path to the directory containing the Terraform blueprint."}},
        )

    def _run(self, blueprint_path: str) -> str:
        """Runs terraform init and apply, capturing output."""
        try:
            # Run terraform init first and check its success
            subprocess.run(["terraform", "init", "-input=false"], cwd=blueprint_path, capture_output=True, text=True, check=True)
            apply_result = subprocess.run(["terraform", "apply", "-auto-approve", "-input=false"], cwd=blueprint_path, capture_output=True, text=True, check=True)
            return f"Terraform apply successful.\nSTDOUT:\n{apply_result.stdout}"
        except subprocess.CalledProcessError as e:
            return f"Terraform command failed with exit code {e.returncode}.\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}"
        except FileNotFoundError:
            return "Error: 'terraform' command not found. Is Terraform installed and in the system's PATH?"
        except Exception as e:
            return f"An unexpected error occurred: {e}"
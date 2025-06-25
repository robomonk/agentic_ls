import json
from pathlib import Path
from google.adk.tools import BaseTool, tool_code

class CreateNextflowConfigTool(BaseTool):
    """
    A tool to generate a nextflow.config file.
    """
    def _get_declaration(self):
        return tool_code(
            name="create_nextflow_config",
            description="Generates a nextflow.config file with specified content and returns its path.",
            parameters={
                "config_content": {
                    "type": "string",
                    "description": "The full content of the nextflow.config file. Example: 'process.executor = \\'local\\''"
                }
            }
        )

    def _run(self, config_content: str) -> str:
        """Writes the config content to a file."""
        # The config_content will now contain the full path
        try:
            config_path = Path(config_content)
            config_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
            config_path.write_text(config_content)
            return f"Successfully created nextflow.config at {str(config_path)}"
        except Exception as e:
            return f"Error creating nextflow.config: {e}"

class CreateParamsJsonTool(BaseTool):
    """
    A tool to generate a params.json file for a Nextflow pipeline.
    """
    def _get_declaration(self):
        return tool_code(
            name="create_params_json",
            description="Creates a params.json file from a dictionary of parameters and returns its path.",
            parameters={
                "params_data": {
                    "type": "object",
                    "description": "A dictionary containing the parameters for the pipeline. Example: {'input': 'data.csv', 'outdir': './results'}"
                }
            }
        )

    def _run(self, params_data: dict) -> str:
        """Writes the parameters dictionary to a JSON file."""
        # The params_data dict will now contain the full path
        try:
            params_path = Path(params_data["path"])
            params_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
            params_path.write_text(json.dumps(params_data["content"], indent=4))  # params_data is a dict
            return f"Successfully created params.json at {str(params_path)}"
        except Exception as e:
            return f"Error creating params.json: {e}"

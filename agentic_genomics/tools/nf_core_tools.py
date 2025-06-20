import requests
import json
from typing import List, Dict, Any
from google.adk.tools import BaseTool

NF_CORE_API_URL = "https://nf-co.re"

class ListNfCorePipelinesTool(BaseTool):
    """Tool to fetch a list of all available nf-core pipelines."""

    def __init__(self):
        super().__init__(
            name="list_nf_core_pipelines",
            description="Fetches a list of all available nf-core pipelines, returning their name and description."
        )

    def run(self) -> List[Dict[str, str]]:
        """
        Fetches a list of all available nf-core pipelines.

        Returns:
            List[Dict[str, str]]: A list of dictionaries, where each dictionary
                                   contains the 'name' and 'description' of a pipeline.
                                   Returns an empty list if an error occurs during JSON decoding.
        Raises:
            requests.exceptions.RequestException: If a network error occurs (excluding JSON decode).
        """
        try:
            response = requests.get(f"{NF_CORE_API_URL}/pipelines.json")
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            pipelines_data = response.json() # This can raise json.JSONDecodeError

            formatted_pipelines = []
            # Ensure 'remote_workflows' key exists and is a list
            remote_workflows = pipelines_data.get("remote_workflows")
            if isinstance(remote_workflows, list):
                for pipeline in remote_workflows:
                    # Ensure each pipeline is a dictionary before trying to get keys
                    if isinstance(pipeline, dict):
                        name = pipeline.get("name", "N/A")
                        description = pipeline.get("description")
                        formatted_pipelines.append({
                            "name": name,
                            "description": description if description is not None else "N/A"
                        })
                    else:
                        # Log or handle malformed pipeline entry if necessary
                        print(f"Skipping malformed pipeline entry: {pipeline}")
            else:
                # Log or handle if 'remote_workflows' is not in the expected format
                print(f"Warning: 'remote_workflows' key missing or not a list in API response.")

            return formatted_pipelines
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response from nf-core pipelines API: {e}")
            return []
        except requests.exceptions.RequestException as e:
            # This will catch other network-related errors like ConnectionError, Timeout, HTTPError
            print(f"Error fetching nf-core pipelines: {e}")
            raise


# Placeholder for GetPipelineSchemaTool - will be implemented in the next step
class GetPipelineSchemaTool(BaseTool):
    """Tool to fetch the schema for a specific nf-core pipeline."""

    def __init__(self):
        super().__init__(
            name="get_pipeline_schema",
            description="Fetches the JSON schema for a specified nf-core pipeline."
        )

    def run(self, pipeline_name: str) -> Dict[str, Any]:
        """
        Fetches the schema for a specific nf-core pipeline.

        Args:
            pipeline_name (str): The name of the pipeline (e.g., 'rnaseq').

        Returns:
            Dict[str, Any]: A dictionary representing the pipeline's schema.
                            Returns an empty dictionary if the pipeline is not found (404)
                            or a JSON decoding error occurs.
        Raises:
            requests.exceptions.RequestException: If a network error occurs (excluding JSON decode and 404s handled by returning {}).
        """
        try:
            url = f"{NF_CORE_API_URL}/api/v2/pipeline_schema/{pipeline_name}"
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for bad status codes (non-404s)
            return response.json() # This can raise json.JSONDecodeError
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"Pipeline schema not found for '{pipeline_name}' (404): {e}")
                return {}
            else:
                # For other HTTP errors (5xx, other 4xx), print and re-raise
                print(f"HTTP error fetching schema for '{pipeline_name}': {e}")
                raise
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response for '{pipeline_name}' schema: {e}")
            return {}
        except requests.exceptions.RequestException as e:
            # This will catch other network-related errors like ConnectionError, Timeout
            print(f"Network error fetching schema for '{pipeline_name}': {e}")
            raise
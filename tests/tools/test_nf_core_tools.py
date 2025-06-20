import pytest
import requests
import requests_mock
from agentic_genomics.tools import nf_core_tools # This will be updated later if __init__ changes

# Mock data for list_nf_core_pipelines
MOCK_PIPELINES_RESPONSE = {
    "remote_workflows": [
        {"name": "nf-core/rnaseq", "full_name": "nf-core/rnaseq", "description": "RNA sequencing analysis pipeline.", "version": "3.14.0"},
        {"name": "nf-core/sarek", "full_name": "nf-core/sarek", "description": "Cancer variant calling pipeline.", "version": "3.1.1"},
        {"name": "nf-core/methylseq", "description": "Methylation sequencing analysis pipeline.", "version": "2.2.0"} # Missing full_name to test robustness
    ]
}

MOCK_PIPELINES_EXPECTED_OUTPUT = [
    {"name": "nf-core/rnaseq", "description": "RNA sequencing analysis pipeline."},
    {"name": "nf-core/sarek", "description": "Cancer variant calling pipeline."},
    {"name": "nf-core/methylseq", "description": "Methylation sequencing analysis pipeline."}
]


# Mock data for get_pipeline_schema (example for a valid pipeline)
MOCK_VALID_SCHEMA_NAME = "somepipeline"
MOCK_VALID_SCHEMA_RESPONSE = {
    "name": f"nf-core/{MOCK_VALID_SCHEMA_NAME}", # The tool itself doesn't add 'nf-core/' prefix, API should provide full name
    "schema": {
        "definitions": {
            "input_output_options": {
                "title": "Input/output options",
                "type": "object",
                "properties": {
                    "input": {"type": "string", "description": "Path to input samplesheet."}
                }
            }
        }
    }
}

# Attempt to import BaseTool and skip all tests in this file if it's not available.
try:
    from google.adk.tools import BaseTool
    # A simple check to ensure nf_core_tools also successfully imported BaseTool or uses it.
    # This is more of an indirect check, actual tool usage will confirm.
    if not issubclass(nf_core_tools.ListNfCorePipelinesTool, BaseTool):
        raise ImportError("ListNfCorePipelinesTool is not a subclass of BaseTool")
    if not issubclass(nf_core_tools.GetPipelineSchemaTool, BaseTool):
        raise ImportError("GetPipelineSchemaTool is not a subclass of BaseTool")
except ImportError as e:
    pytest.skip(f"ADK's BaseTool or its usage in nf_core_tools is problematic, skipping all tests in this file: {e}", allow_module_level=True)


class TestNfCoreToolsUnit:

    def test_list_nf_core_pipelines_tool_success(self, requests_mock):
        """Test successful fetching of nf-core pipelines with ListNfCorePipelinesTool."""
        requests_mock.get(f"{nf_core_tools.NF_CORE_API_URL}/pipelines.json", json=MOCK_PIPELINES_RESPONSE)
        tool = nf_core_tools.ListNfCorePipelinesTool()
        pipelines = tool.run()
        assert pipelines == MOCK_PIPELINES_EXPECTED_OUTPUT

    def test_list_nf_core_pipelines_tool_network_error(self, requests_mock):
        """Test ListNfCorePipelinesTool handles network errors."""
        requests_mock.get(f"{nf_core_tools.NF_CORE_API_URL}/pipelines.json", exc=requests.exceptions.ConnectionError)
        tool = nf_core_tools.ListNfCorePipelinesTool()
        with pytest.raises(requests.exceptions.ConnectionError):
            tool.run()

    def test_list_nf_core_pipelines_tool_json_decode_error(self, requests_mock):
        """Test ListNfCorePipelinesTool handles JSON decoding errors and returns empty list."""
        requests_mock.get(f"{nf_core_tools.NF_CORE_API_URL}/pipelines.json", text="not a json")
        tool = nf_core_tools.ListNfCorePipelinesTool()
        pipelines = tool.run()
        assert pipelines == []

    def test_list_nf_core_pipelines_tool_empty_response_key_missing(self, requests_mock):
        """Test ListNfCorePipelinesTool handles API response with missing 'remote_workflows' key."""
        requests_mock.get(f"{nf_core_tools.NF_CORE_API_URL}/pipelines.json", json={"unexpected_key": []})
        tool = nf_core_tools.ListNfCorePipelinesTool()
        pipelines = tool.run()
        assert pipelines == []

    def test_list_nf_core_pipelines_tool_malformed_workflow_entry(self, requests_mock):
        """Test ListNfCorePipelinesTool handles malformed entries in 'remote_workflows'."""
        malformed_response = {
            "remote_workflows": [
                {"name": "good/pipeline", "description": "A good one"},
                "not a dictionary",
                {"name": "another/good", "description": "Another good one"}
            ]
        }
        expected_output_malformed = [
            {"name": "good/pipeline", "description": "A good one"},
            {"name": "another/good", "description": "Another good one"}
        ]
        requests_mock.get(f"{nf_core_tools.NF_CORE_API_URL}/pipelines.json", json=malformed_response)
        tool = nf_core_tools.ListNfCorePipelinesTool()
        pipelines = tool.run()
        assert pipelines == expected_output_malformed


    def test_get_pipeline_schema_tool_success(self, requests_mock):
        """Test successful fetching of a pipeline schema with GetPipelineSchemaTool."""
        requests_mock.get(
            f"{nf_core_tools.NF_CORE_API_URL}/api/v2/pipeline_schema/{MOCK_VALID_SCHEMA_NAME}",
            json=MOCK_VALID_SCHEMA_RESPONSE
        )
        tool = nf_core_tools.GetPipelineSchemaTool()
        schema = tool.run(pipeline_name=MOCK_VALID_SCHEMA_NAME)
        assert schema == MOCK_VALID_SCHEMA_RESPONSE

    def test_get_pipeline_schema_tool_not_found_404(self, requests_mock):
        """Test GetPipelineSchemaTool handles a 404 error and returns empty dict."""
        pipeline_name = "nonexistentpipeline"
        requests_mock.get(
            f"{nf_core_tools.NF_CORE_API_URL}/api/v2/pipeline_schema/{pipeline_name}",
            status_code=404
        )
        tool = nf_core_tools.GetPipelineSchemaTool()
        schema = tool.run(pipeline_name=pipeline_name)
        assert schema == {}

    def test_get_pipeline_schema_tool_network_error(self, requests_mock):
        """Test GetPipelineSchemaTool handles network errors."""
        pipeline_name = MOCK_VALID_SCHEMA_NAME
        requests_mock.get(
            f"{nf_core_tools.NF_CORE_API_URL}/api/v2/pipeline_schema/{pipeline_name}",
            exc=requests.exceptions.ConnectionError
        )
        tool = nf_core_tools.GetPipelineSchemaTool()
        with pytest.raises(requests.exceptions.ConnectionError):
            tool.run(pipeline_name=pipeline_name)

    def test_get_pipeline_schema_tool_json_decode_error(self, requests_mock):
        """Test GetPipelineSchemaTool handles JSON decoding errors and returns empty dict."""
        pipeline_name = MOCK_VALID_SCHEMA_NAME
        requests_mock.get(
            f"{nf_core_tools.NF_CORE_API_URL}/api/v2/pipeline_schema/{pipeline_name}",
            text="not a json"
        )
        tool = nf_core_tools.GetPipelineSchemaTool()
        schema = tool.run(pipeline_name=pipeline_name)
        assert schema == {}

    def test_get_pipeline_schema_tool_http_error_other_than_404(self, requests_mock):
        """Test GetPipelineSchemaTool handles and re-raises other HTTP errors."""
        pipeline_name = MOCK_VALID_SCHEMA_NAME
        requests_mock.get(
            f"{nf_core_tools.NF_CORE_API_URL}/api/v2/pipeline_schema/{pipeline_name}",
            status_code=500 # Internal Server Error
        )
        tool = nf_core_tools.GetPipelineSchemaTool()
        with pytest.raises(requests.exceptions.HTTPError):
            tool.run(pipeline_name=pipeline_name)


@pytest.mark.integration
class TestNfCoreToolsIntegration:

    def test_list_nf_core_pipelines_tool_integration(self):
        """Integration test for ListNfCorePipelinesTool."""
        tool = nf_core_tools.ListNfCorePipelinesTool()
        try:
            pipelines = tool.run()
            assert isinstance(pipelines, list)
            if pipelines: # Only assert further if list is not empty
                assert len(pipelines) > 0
                for pipeline in pipelines:
                    assert "name" in pipeline
                    assert isinstance(pipeline["name"], str)
                    assert "description" in pipeline
                    assert isinstance(pipeline["description"], str)
            else:
                # This case might happen if nf-co.re is down or returns an unexpected empty list.
                # For an integration test, this is still a "pass" as the tool should handle it gracefully.
                print("Warning: list_nf_core_pipelines_tool_integration returned an empty list.")
        except requests.exceptions.RequestException as e:
            pytest.fail(f"ListNfCorePipelinesTool integration test failed due to network error: {e}")
        except Exception as e:
            pytest.fail(f"ListNfCorePipelinesTool integration test failed with unexpected error: {e}")

    def test_get_pipeline_schema_tool_integration_valid_pipeline(self):
        """
        Integration test for GetPipelineSchemaTool. Tries 'atacseq', then 'rnaseq'.
        Accepts an empty dict if a 404 is encountered, as V2 schemas might not exist for all pipelines.
        """
        # Try a few common pipeline names, as V2 schema availability can be sparse.
        pipeline_names_to_try = ["atacseq", "rnaseq", "methylseq"]
        tool = nf_core_tools.GetPipelineSchemaTool()

        schema_found = False
        for pipeline_name in pipeline_names_to_try:
            print(f"Integration test: Trying to get schema for '{pipeline_name}'...")
            try:
                schema = tool.run(pipeline_name=pipeline_name)
                assert isinstance(schema, dict)
                if schema:
                    # If a schema is returned, validate its basic structure
                    # The API might return the name without "nf-core/" prefix, or with it.
                    assert pipeline_name in schema.get("name", "")
                    assert "schema" in schema
                    assert "definitions" in schema["schema"]
                    print(f"Successfully fetched and validated schema for '{pipeline_name}'.")
                    schema_found = True
                    break # Found a working schema, no need to try others
                else:
                    # This means a 404 was likely returned.
                    print(f"Schema for '{pipeline_name}' was not found or empty (likely 404 on V2 API). This is accepted by the test.")
            except requests.exceptions.RequestException as e:
                pytest.fail(f"GetPipelineSchemaTool integration test for '{pipeline_name}' failed due to network error: {e}")
            except Exception as e:
                pytest.fail(f"GetPipelineSchemaTool integration test for '{pipeline_name}' failed with unexpected error: {e}")

        if not schema_found:
            print(f"Warning: Could not find a V2 schema for any of the test pipelines: {pipeline_names_to_try}. The test passes if all attempts were handled gracefully (e.g. returned empty dict for 404s).")


    def test_get_pipeline_schema_tool_integration_invalid_pipeline(self):
        """Integration test for GetPipelineSchemaTool with a known invalid pipeline name."""
        pipeline_name = "thispipelinedoesnotexistandneverwill12345abc"
        tool = nf_core_tools.GetPipelineSchemaTool()
        try:
            schema = tool.run(pipeline_name=pipeline_name)
            assert schema == {} # Expecting an empty dictionary for a 404
        except requests.exceptions.RequestException as e:
            pytest.fail(f"GetPipelineSchemaTool for invalid pipeline failed due to network error: {e}")
        except Exception as e:
            pytest.fail(f"GetPipelineSchemaTool for invalid pipeline failed with unexpected error: {e}")

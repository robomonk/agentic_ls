from google.adk.tools import BaseTool
from google.adk.tools import tool_code

# In a real scenario, you'd use 'requests' or 'nf-core' CLI wrapper here.
# For demonstration, we'll use mock data.
MOCK_NF_CORE_PIPELINES = [
    {"name": "nf-core/rnaseq", "description": "RNA-Seq analysis pipeline"},
    {"name": "nf-core/sarek", "description": "Variant calling pipeline for germline and somatic variants"},
    {"name": "nf-core/chipseq", "description": "ChIP-Seq analysis pipeline"},
    {"name": "nf-core/atacseq", "description": "ATAC-Seq analysis pipeline"},
    {"name": "nf-core/mag", "description": "Metagenome-assembled genomes (MAGs) pipeline"},
]

MOCK_PIPELINE_SCHEMAS = {
    "nf-core/rnaseq": {
        "input": {"type": "string", "description": "Path to input samplesheet.csv"},
        "outdir": {"type": "string", "description": "The output directory where the results will be saved"},
        "genome": {"type": "string", "description": "Reference genome ID (e.g., GRCh38)"},
        "single_end": {"type": "boolean", "description": "Specify if input reads are single-end"},
    },
    "nf-core/sarek": {
        "input": {"type": "string", "description": "Path to input samplesheet.csv"},
        "outdir": {"type": "string", "description": "The output directory where the results will be saved"},
        "genome": {"type": "string", "description": "Reference genome ID (e.g., GRCh38)"},
        "tools": {"type": "array", "description": "List of variant calling tools to run (e.g., 'mutect2', 'strelka')"},
    },
}

class ListNfCorePipelinesTool(BaseTool):
    """
    A tool to list available nf-core pipelines with their descriptions.
    """
    def _get_declaration(self):
        return tool_code(
            name="list_nf_core_pipelines",
            description="Lists all available nf-core pipelines and their brief descriptions.",
            parameters={}
        )

    def _run(self):
        # In a real implementation, this would call the nf-core API or parse local data.
        # Example: response = requests.get("https://nf-co.re/pipelines.json")
        # return response.json()
        return MOCK_NF_CORE_PIPELINES

class GetPipelineSchemaTool(BaseTool):
    """
    A tool to retrieve the input schema (parameters) for a specific nf-core pipeline.
    """
    def _get_declaration(self):
        return tool_code(
            name="get_pipeline_schema",
            description="Retrieves the detailed input schema (parameters) for a given nf-core pipeline.",
            parameters={"pipeline_name": {"type": "string", "description": "The full name of the nf-core pipeline (e.g., 'nf-core/rnaseq')."}}
        )

    def _run(self, pipeline_name: str):
        # In a real implementation, this would parse nextflow_schema.json or call an API.
        return MOCK_PIPELINE_SCHEMAS.get(pipeline_name, {"error": f"Schema not found for {pipeline_name}"})
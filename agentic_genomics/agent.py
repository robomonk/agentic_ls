
from google.adk.agents import LlmAgent  
from google.adk.tools import get_user_choice  
# from .agents.pipeline_scout import PipelineScoutAgent  # Temporarily commented out - Not implemented
# from .tools.deployment_workflow import DeploymentWorkflowTool  # Temporarily commented out - Not implemented
  
root_agent = LlmAgent(  
    name="orchestrator_agent",  
    model='gemini-2.5-pro-preview-05-06',
    description="Orchestrates bioinformatics pipeline deployment",  
    instruction="""  
    You are a bioinformatics pipeline orchestrator. You help users:  
    1. Discover and understand nf-core pipelines  
    2. Configure pipeline parameters with human approval  
    3. Deploy pipelines to cloud infrastructure  
      
    Always ask for user confirmation before proceeding with deployment steps.  
    """,  
    tools=[  
        # Pipeline discovery tools are expected to be the ones implemented (ListNfCorePipelinesTool, GetPipelineSchemaTool)
        # These will be added to an agent's tool list when the agent is defined or used.
        # Human-in-the-loop tools  
        get_user_choice,  
        # Workflow execution tool  
        # DeploymentWorkflowTool(), # Temporarily commented out - Not implemented
    ],  
    sub_agents=[  
        # PipelineScoutAgent(), # Temporarily commented out - Not implemented
    ]  
)
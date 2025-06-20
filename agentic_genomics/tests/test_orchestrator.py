import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the project root to the Python path to allow importing agentic_genomics
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from agentic_genomics.agent import OrchestratorAgent
from adk.llm import DefaultLLMProvider # Using DefaultLLMProvider for testing placeholders

# Load environment variables from .env file in the agentic_genomics directory
dotenv_path = os.path.join(project_root, 'agentic_genomics', '.env')
load_dotenv(dotenv_path=dotenv_path)

print(f"--- test_orchestrator.py: Attempting to load .env from: {dotenv_path} ---")
print(f"--- test_orchestrator.py: GCP_PROJECT_ID (from env): {os.getenv('GCP_PROJECT_ID')} ---")


async def main():
    print("\n--- test_orchestrator.py: Starting Test ---")

    # For placeholder testing, DefaultLLMProvider is sufficient as no actual LLM calls are made.
    # If actual LLM integration was being tested, a mock or a configured provider would be needed.
    llm_provider = DefaultLLMProvider()

    # Instantiate the OrchestratorAgent
    # Provide an agent_name for clarity in logs if the agent's __init__ expects it or uses it.
    orchestrator = OrchestratorAgent(llm_provider=llm_provider, agent_name="TestOrchestrator")
    print("--- test_orchestrator.py: OrchestratorAgent instantiated ---")

    # Define a sample user query
    user_query = "Deploy a test variant calling pipeline for sample X."
    print(f"--- test_orchestrator.py: Calling OrchestratorAgent with query: '{user_query}' ---")

    # Call the OrchestratorAgent's primary skill
    # The `aask` method is the standard way to interact with an ADK agent.
    # Alternatively, can call the specific skill `run_genomics_deployment_workflow` directly if needed for testing.
    # response_str = await orchestrator.aask(query=user_query)

    # For this iteration, calling the skill directly to better see the structured output
    response_dict = await orchestrator.run_genomics_deployment_workflow(user_query=user_query)

    print("\n--- test_orchestrator.py: OrchestratorAgent call complete ---")
    print("--- test_orchestrator.py: Final Response from Orchestrator ---")

    import json
    print(json.dumps(response_dict, indent=2))

    # Success Criteria Verification (based on print statements for this iteration):
    # 1. Project structure: Assumed correct by this point.
    # 2. Environment: Assumed active.
    # 3. OrchestratorAgent instantiation: Verified by print statement.
    # 4. Sequential execution triggered: Verify by checking for print statements from:
    #    - OrchestratorAgent initiating workflow
    #    - DeploymentWorkflow starting
    #    - PipelineScoutAgent skill & tool
    #    - ConfiguratorAgent skill & tool
    #    - BlueprintArchitectAgent skill & tool
    #    - DeploymentEngineerAgent skill & tool
    #    - DeploymentWorkflow completing
    #    - OrchestratorAgent completing
    # 5. Placeholder tool methods called: Verified by their respective print statements.
    # 6. No major import/class definition errors: If the script runs to this point, this is largely met.

    print("\n--- test_orchestrator.py: Test Finished ---")
    print("--- Please check the console output for print statements from each agent and tool to verify the workflow. ---")

if __name__ == "__main__":
    # Ensure an event loop is available for asyncio.run
    # In some environments (like older Python versions or specific IDEs),
    # setting the policy explicitly can help.
    if sys.platform == "win32" and sys.version_info >= (3, 8):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())

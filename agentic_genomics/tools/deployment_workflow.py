import asyncio
from adk.agent import SequentialAgent, AgentNotRegisteredError
from adk.llm import LLMProvider
from agentic_genomics.agents import (
    PipelineScoutAgent,
    ConfiguratorAgent,
    BlueprintArchitectAgent,
    DeploymentEngineerAgent
)
from typing import Dict, Any, Optional

class DeploymentWorkflow(SequentialAgent):
    def __init__(self, llm_provider: LLMProvider, **kwargs):
        name = kwargs.pop('name', "DeploymentWorkflow")
        super().__init__(llm_provider=llm_provider, name=name, **kwargs)
        print(f"DeploymentWorkflow '{self.name}' initializing...")

        self.scout = PipelineScoutAgent(llm_provider=llm_provider, agent_name="PipelineScout")
        self.configurator = ConfiguratorAgent(llm_provider=llm_provider, agent_name="PipelineConfigurator")
        self.architect = BlueprintArchitectAgent(llm_provider=llm_provider, agent_name="BlueprintArchitect")
        self.engineer = DeploymentEngineerAgent(llm_provider=llm_provider, agent_name="DeploymentEngineer")

        self.add_agents([
            self.scout,
            self.configurator,
            self.architect,
            self.engineer
        ])
        print(f"DeploymentWorkflow '{self.name}': Agents added to sequence: Scout -> Configurator -> Architect -> Engineer.")

    def run(self, initial_input: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        print(f"\nDeploymentWorkflow '{self.name}': Synchronous run starting with initial input: {initial_input}")

        current_context = initial_input
        final_output = None

        for agent_name_in_sequence in self._agent_sequence:
            agent = self._agents.get(agent_name_in_sequence)
            if not agent:
                print(f"DeploymentWorkflow '{self.name}': Error - Agent '{agent_name_in_sequence}' not found.")
                raise AgentNotRegisteredError(f"Agent '{agent_name_in_sequence}' not found.")

            print(f"\nDeploymentWorkflow '{self.name}': Executing agent: {agent.agent_name} with input: {current_context}")

            mock_skill_output = {}
            skill_was_run = False
            try:
                # This is a simplified way to call the async skills for this placeholder iteration.
                # It assumes that the OrchestratorAgent is running this `run` method in a separate thread
                # or that the environment can handle `asyncio.run` calls within this synchronous method.
                if isinstance(agent, PipelineScoutAgent):
                    query = current_context.get("query", "") if isinstance(current_context, dict) else str(current_context)
                    mock_skill_output = asyncio.run(agent.discover_available_pipelines(query=query))
                    skill_was_run = True
                elif isinstance(agent, ConfiguratorAgent):
                    discovered_pipelines = current_context.get("discovered_pipelines", [])
                    user_prefs = current_context.get("user_preferences", {})
                    mock_skill_output = asyncio.run(agent.configure_selected_pipeline(discovered_pipelines=discovered_pipelines, user_preferences=user_prefs))
                    skill_was_run = True
                elif isinstance(agent, BlueprintArchitectAgent):
                    configured_data = current_context
                    mock_skill_output = asyncio.run(agent.generate_deployment_blueprint(configured_pipeline_data=configured_data))
                    skill_was_run = True
                elif isinstance(agent, DeploymentEngineerAgent):
                    blueprint_data = current_context
                    mock_skill_output = asyncio.run(agent.deploy_and_execute_pipeline(blueprint_data=blueprint_data))
                    skill_was_run = True
                else:
                    print(f"DeploymentWorkflow '{self.name}': Error - Unknown agent type {type(agent)}.")
                    return {"error": f"Unknown agent type {type(agent)}"}

                if skill_was_run:
                    print(f"DeploymentWorkflow '{self.name}': Agent '{agent.agent_name}' raw skill output: {mock_skill_output}")
                    processed_output = agent.process_run_output(mock_skill_output)
                    print(f"DeploymentWorkflow '{self.name}': Agent '{agent.agent_name}' processed output for next agent: {processed_output}")
                    current_context = processed_output
                    final_output = current_context
                else: # Should not happen if agent types are known
                    return {"error": f"Skill not run for agent {agent.agent_name}"}


            except Exception as e:
                print(f"DeploymentWorkflow '{self.name}': Error during execution of agent {agent.agent_name}: {e}")
                import traceback
                traceback.print_exc()
                return {"error": f"Error in agent {agent.agent_name}: {str(e)}", "details": traceback.format_exc()}

        print(f"\nDeploymentWorkflow '{self.name}': Synchronous run completed. Final output: {final_output}")
        return final_output

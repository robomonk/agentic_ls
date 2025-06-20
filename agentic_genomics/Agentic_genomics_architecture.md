# Agentic Genomics Requirements and Design Document

**1. Introduction**

This document outlines the requirements and design for `agentic_genomics`, a multi-agent system built using the Google Agent Development Kit (ADK) to automate the process of selecting, configuring, and deploying Nextflow pipelines on cloud infrastructure for genomic analysis. The system aims to streamline the execution of complex bioinformatics workflows by leveraging specialized AI agents.

**1.1. Purpose**

The purpose of this document is to:
* Define the functional and non-functional requirements of the `agentic_genomics` system.
* Describe the architectural design and how it utilizes the Google ADK.
* Detail the responsibilities, skills, and interactions of each agent.
* Specify the design of custom tools for integration with bioinformatics platforms (nf-core, Nextflow, Terraform).
* Outline key considerations for data flow, error handling, state management, and security.

**1.2. Scope**

The initial scope of `agentic_genomics` is to automate the following process:
1. Receive a user request specifying a genomic analysis task.
2. Identify suitable Nextflow pipelines from nf-core based on the request.
3. Configure the selected Nextflow pipeline with user-provided parameters and resource requirements.
4. Generate infrastructure-as-code (Terraform) to provision a cloud-based cluster suitable for running the pipeline.
5. Deploy the cloud cluster using the generated blueprint.
6. Provide the user with the necessary information to execute the Nextflow pipeline on the provisioned cluster.
7. Executing the Nextflow pipeline on the cluster.

**Out of Scope for Initial Release:**
* Monitoring the running Nextflow job.
* Analyzing pipeline outputs.
* Supporting multiple cloud providers simultaneously (focus on Google Cloud Platform initially).
* Supporting Nextflow pipelines from sources other than nf-core initially.

**1.3. Definitions and Acronyms**

* **ADK:** Google Agent Development Kit
* **LLM:** Large Language Model
* **nf-core:** A community effort to build curated Nextflow pipelines.
* **Nextflow:** A workflow management system for computational pipelines.
* **Terraform:** An infrastructure-as-code tool.
* **GCP:** Google Cloud Platform

**2. Requirements**

**2.1. Functional Requirements**

* **FR1: Pipeline Selection:** The system shall be able to identify relevant nf-core pipelines based on a natural language description of the required genomic analysis.
* **FR2: Pipeline Parameter Configuration:** The system shall allow users to specify parameters for the selected Nextflow pipeline and validate user input against the pipeline schema.
* **FR3: Resource Requirement Estimation:** The system shall be able to estimate the computational resources (CPU, memory, disk) required for the configured pipeline based on input data size and pipeline complexity.
* **FR4: Infrastructure Blueprint Generation:** The system shall generate a Terraform blueprint that defines the cloud infrastructure required to run the configured Nextflow pipeline.
* **FR5: Cloud Cluster Deployment:** The system shall be able to execute the generated Terraform blueprint to provision the cloud infrastructure on GCP.
* **FR6: User Interaction:** The system shall provide a mechanism for users to provide input (analysis request, parameters) and receive output (selected pipeline, cluster details, status updates).
* **FR7: Human-in-the-Loop Validation:** The system shall allow for human review and approval of critical steps (e.g., pipeline selection, estimated resources, infrastructure costs) before proceeding.
* **FR8: Error Reporting:** The system shall report errors encountered during any stage of the workflow to the user.
* **FR9: Workflow Tracking:** The system shall provide a mechanism to track the progress of the overall workflow.

**2.2. Non-Functional Requirements**

* **NFR1: Reliability:** The system shall be reliable in executing the steps of the workflow and handling expected errors gracefully.
* **NFR2: Maintainability:** The codebase shall be modular and well-documented to facilitate future maintenance and extensions.
* **NFR3: Security:** The system shall handle cloud credentials and sensitive information securely. Data access and permissions shall be appropriately managed.
* **NFR4: Performance:** The system should complete the workflow within a reasonable time frame, considering the inherent delays in cloud provisioning.
* **NFR5: Scalability (Future):** The architecture should be designed to allow for future scalability to handle more concurrent requests and potentially larger deployments.
* **NFR6: Reproducibility (Future):** The system should aim to provide mechanisms for reproducing the infrastructure and configuration used for a specific analysis.

**3. Architectural Design**

**3.1. High-Level Architecture**

The `agentic_genomics` system follows a multi-agent architecture orchestrated by a central `OrchestratorAgent`. The workflow is primarily executed sequentially by specialized sub-agents.

+-----------------------+
|   User/External System|
+-----------+-----------+
|
| Request (Analysis Task)
v
+-----------------------+
| OrchestratorAgent     |
| (ADK Root Agent)      |
+-----------+-----------+
|
| Delegates Tasks
v
+-------------------------------------------------------------+
| Sequential Deployment Workflow (SequentialAgent)          |
|                                                             |
| +-------------------+   +-------------------+   +---------------------+   +---------------------+ |
| | PipelineScoutAgent|-->| ConfiguratorAgent |-->| BlueprintArchitect |-->| DeploymentEngineer  | |
| | (LLM Agent)       |   | (LLM Agent)       |   | (LLM Agent)         |   | (LLM Agent)         | |
| |                   |   |                   |   |                     |   |                     | |
| +---------+---------+   +---------+---------+   +-----------+---------+   +-----------+---------+ |
|           |                       |                       |                       |             |
|           | Uses Tools            | Uses Tools            | Uses Tools            | Uses Tools  |
|           v                       v                       v                       v             v
| +---------+---------+ +---------+---------+ +-----------+---------+ +-----------+---------+ |
| | nf-core Tools     | | Nextflow Tools    | | Terraform Tools     | | Terraform Tools     | |
| | (Custom ADK Tools)| | (Custom ADK Tools)| | (Custom ADK Tools)  | | (Custom ADK Tools)  | |
| +-------------------+ +-------------------+ +---------------------+ +---------------------+ |
+---------------------------------------------------------------------------------------------+
|
| Status/Results
v
+-----------------------+
|   User/External System|
+-----------------------+


**3.2. Agent Design (ADK Implementation)**

*   **OrchestratorAgent (`agent.py`):**
    *   **Type:** ADK Root Agent, potentially an `LlmAgent` with orchestration capabilities.
    *   **Role:** Receives initial requests, manages the overall workflow lifecycle, delegates tasks to the Sequential Deployment Workflow, handles high-level errors, and reports results.
    *   **Skills:**
        *   `start_deployment_workflow(request: str)`: Initiates the sequential workflow.
        *   `handle_workflow_completion(status: str, results: dict)`: Processes the final status and results from the sequential agent.
        *   `handle_workflow_error(error: str)`: Manages errors reported by the sequential agent.
    *   **Memory:** Stores the initial request, a reference to the Sequential Deployment Workflow agent, and overall workflow status.
    *   **Tools:** Potentially uses a `transfer_to_agent_tool` to delegate to the Sequential Deployment Workflow.

*   **Sequential Deployment Workflow (`tools/deployment_workflow.py` - Wrapper around `SequentialAgent`):**
    *   **Type:** Wraps an ADK `SequentialAgent`.
    *   **Role:** Executes the sub-agents (`PipelineScoutAgent`, `ConfiguratorAgent`, `BlueprintArchitectAgent`, `DeploymentEngineerAgent`) in a predefined sequence.
    *   **Sub-Agents:** Manages instances of the specialized agents.
    *   **Execution Flow:** Defines the order of execution:
        1.  `PipelineScoutAgent`
        2.  `ConfiguratorAgent`
        3.  `BlueprintArchitectAgent`
        4.  `DeploymentEngineerAgent`
    *   **Data Flow:** Passes outputs from one agent as inputs to the next in the sequence.

*   **PipelineScoutAgent (`agents/pipeline_scout.py`):**
    *   **Type:** ADK `LlmAgent`.
    *   **Role:** Interprets the user's request using an LLM to identify relevant nf-core pipelines. Uses custom tools to interact with nf-core data.
    *   **Skills:**
        *   `find_pipeline(analysis_request: str)`: Uses the LLM and `nf_core_tools` to identify suitable pipelines.
    *   **Memory:** Stores the analysis request and potential pipeline candidates.
    *   **Tools:**
        *   `nf_core_tools.list_nf_core_pipelines`: Custom tool to fetch a list of available nf-core pipelines.
        *   `nf_core_tools.get_pipeline_schema`: Custom tool to retrieve the schema (parameters, inputs) of a specific pipeline.
        *   Potentially `get_user_choice_tool` for confirming the selected pipeline with the user (Human-in-the-Loop).

*   **ConfiguratorAgent (`agents/configurator.py`):**
    *   **Type:** ADK `LlmAgent`.
    *   **Role:** Configures the selected Nextflow pipeline based on user input and potentially estimates resource requirements.
    *   **Skills:**
        *   `configure_pipeline(pipeline_details: dict, user_params: dict)`: Uses the LLM and `nextflow_tools` to generate the `nextflow.config` and `params.json`.
        *   `estimate_resources(pipeline_details: dict, user_params: dict)`: (Future) Uses the LLM and potentially custom logic/tools to estimate resource needs.
    *   **Memory:** Stores pipeline details, user parameters, and generated configuration.
    *   **Tools:**
        *   `nextflow_tools.create_nextflow_config`: Custom tool to generate the `nextflow.config` file.
        *   `nextflow_tools.create_params_json`: Custom tool to generate the `params.json` file for pipeline parameters.
        *   Potentially custom tools for resource estimation.
        *   Potentially `get_user_choice_tool` for parameter validation and cost approval.

*   **BlueprintArchitectAgent (`agents/blueprint_architect.py`):**
    *   **Type:** ADK `LlmAgent`.
    *   **Role:** Generates the Terraform blueprint based on resource requirements and target GCP environment.
    *   **Skills:**
        *   `create_blueprint(resource_requirements: dict, gcp_config: dict)`: Uses the LLM and `terraform_tools` to generate the Terraform files.
    *   **Memory:** Stores resource requirements and GCP configuration.
    *   **Tools:**
        *   `terraform_tools.create_nextflow_blueprint`: Custom tool to generate Terraform files (e.g., `main.tf`, `variables.tf`). This tool should encapsulate the logic for defining VM instances, storage buckets, networking, etc., suitable for Nextflow execution.

*   **DeploymentEngineerAgent (`agents/deployment_engineer.py`):**
    *   **Type:** ADK `LlmAgent`.
    *   **Role:** Executes the Terraform blueprint to provision the GCP cluster.
    *   **Skills:**
        *   `deploy_cluster(blueprint_path: str)`: Uses the LLM and `terraform_tools` to apply the Terraform blueprint.
        *   `monitor_deployment(deployment_id: str)`: (Future) Monitors the status of the Terraform deployment.
        *   `get_cluster_details(deployment_id: str)`: Retrieves connection details after successful deployment.
    *   **Memory:** Stores the blueprint path and deployment status.
    *   **Tools:**
        *   `terraform_tools.execute_terraform_apply`: Custom tool to run `terraform apply`.
        *   Potentially custom tools for monitoring Terraform outputs and retrieving cluster details.

**3.3. Custom Tool Design (`tools/`)**

Custom tools will be implemented by inheriting from `adk.tools.BaseTool`.

*   **`nf_core_tools.py`:**
    *   **`list_nf_core_pipelines`:**
        *   **Functionality:** Interacts with the nf-core API or a local cache/clone of nf-core repositories to list available pipelines and their basic descriptions.
        *   **Implementation:** Might use `requests` to interact with the nf-core API or standard library functions for filesystem interaction if using a local clone.
    *   **`get_pipeline_schema`:**
        *   **Functionality:** Retrieves the parameters and input schema for a specific nf-core pipeline. This information is crucial for the `ConfiguratorAgent`.
        *   **Implementation:** Parses the pipeline's `nextflow_schema.json` file (if using a local clone) or interacts with an nf-core API endpoint that provides this information.

*   **`nextflow_tools.py`:**
    *   **`create_nextflow_config`:**
        *   **Functionality:** Generates or modifies a `nextflow.config` file based on the selected profile, resource configurations, and other settings.
        *   **Implementation:** Uses string formatting or configuration file manipulation libraries to create the file content.
    *   **`create_params_json`:**
        *   **Functionality:** Creates a `params.json` file containing the user-provided parameters for the Nextflow pipeline.
        *   **Implementation:** Uses the `json` library to create the JSON file content.

*   **`terraform_tools.py`:**
    *   **`create_nextflow_blueprint`:**
        *   **Functionality:** Generates the Terraform files (`.tf`) required to provision the GCP resources. This tool will need to understand common patterns for deploying Nextflow on GCP (e.g., VM with Docker/Singularity, shared storage like Filestore or NFS, potential use of Google Life Sciences API).
        *   **Implementation:** Might use template engines (like Jinja2) or Python libraries for programmatically generating Terraform code based on input parameters (VM size, disk size, number of nodes, region, etc.).
    *   **`execute_terraform_apply`:**
        *   **Functionality:** Executes the `terraform apply` command within the directory containing the generated blueprint.
        *   **Implementation:** Uses the `subprocess` module to run the Terraform CLI. Will need to handle standard output and errors. Requires GCP authentication to be set up in the environment where the agent is running.

**3.4. Data Flow and Communication**

*   **Initial Request:** User sends a natural language request to the `OrchestratorAgent`.
*   **Orchestrator -> Sequential Workflow:** `OrchestratorAgent` initiates the `SequentialAgent` for deployment, passing the user request.
*   **Sequential Workflow -> PipelineScout:** `SequentialAgent` passes the user request to the `PipelineScoutAgent`.
*   **PipelineScout -> Sequential Workflow:** `PipelineScoutAgent` returns the selected pipeline details (name, version, schema) to the `SequentialAgent`.
*   **Sequential Workflow -> Configurator:** `SequentialAgent` passes the selected pipeline details and user parameters (received from initial request or via Human-in-the-Loop) to the `ConfiguratorAgent`.
*   **Configurator -> Sequential Workflow:** `ConfiguratorAgent` returns the paths to the generated `nextflow.config` and `params.json` files, along with estimated resource requirements (if implemented).
*   **Sequential Workflow -> BlueprintArchitect:** `SequentialAgent` passes the resource requirements and configuration file paths to the `BlueprintArchitectAgent`.
*   **BlueprintArchitect -> Sequential Workflow:** `BlueprintArchitectAgent` returns the path to the generated Terraform blueprint directory.
*   **Sequential Workflow -> DeploymentEngineer:** `SequentialAgent` passes the blueprint directory path to the `DeploymentEngineerAgent`.
*   **DeploymentEngineer -> Sequential Workflow:** `DeploymentEngineerAgent` returns the status of the deployment (success/failure) and relevant cluster connection details (e.g., public IP, SSH command).
*   **Sequential Workflow -> Orchestrator:** `SequentialAgent` returns the final status and cluster details to the `OrchestratorAgent`.
*   **Orchestrator -> User:** `OrchestratorAgent` reports the final status and cluster details to the user.
*   **Error Reporting:** Agents will report errors to the `SequentialAgent`, which in turn reports them to the `OrchestratorAgent` for user notification.
*   **Human-in-the-Loop:** When a Human-in-the-Loop tool is used, the agent pauses and waits for user input via the ADK's mechanism.

**3.5. State Management**

*   **Within Agents:** Agents will use their internal memory (provided by ADK) to store conversational history, task-specific parameters, and intermediate results.
*   **Workflow State:** The `SequentialAgent` inherently manages the state of which sub-agent is currently executing. The `OrchestratorAgent` keeps track of the overall workflow status.
*   **Persistence (Future Consideration):** For long-running deployments, consider adding a mechanism to persist the workflow state to a database or file system so that it can be resumed if interrupted.

**3.6. Error Handling**

*   **Agent-Level:** Each agent should implement error handling within its skills and tool interactions (e.g., catching exceptions from tool calls, handling unexpected LLM responses).
*   **Sequential Workflow:** The `SequentialAgent` will handle errors from its sub-agents and stop the sequence if a critical error occurs.
*   **Orchestrator Level:** The `OrchestratorAgent` will receive error notifications from the sequential workflow and report them to the user.
*   **Specific Error Scenarios:**
    *   **Tool Execution Errors:** Capture stderr and error codes from tool executions (Terraform, Nextflow CLI calls).
    *   **LLM Errors:** Handle cases where the LLM fails to generate a valid response or generates an irrelevant response. Retry with different prompts or fall back to deterministic logic if possible.
    *   **Validation Errors:** Implement checks for invalid user input or incompatible configurations.

**3.7. Security**

*   **Credential Management:** Cloud provider credentials (GCP service account keys or environment variables) should be managed securely outside the application code (e.g., using environment variables, secrets managers like Google Secret Manager). The `DeploymentEngineerAgent` needs access to these.
*   **Least Privilege:** The service account or user running the `agentic_genomics` system should have only the necessary permissions to perform its tasks (e.g., create VMs, storage, networking in a specific GCP project).
*   **Data Handling:** Avoid storing sensitive genomic data within the agent's memory or persistent storage unless absolutely necessary and with appropriate security measures. The system primarily orchestrates the provisioning of infrastructure to process the data, not the data processing itself.

**4. Project Structure and Implementation Notes**

*   **`agentic_genomics/`:**
    *   `__init__.py`: Standard Python package file.
    *   `agent.py`: Contains the `OrchestratorAgent`.
    *   `agents/`: Directory for specialized agents.
        *   `__init__.py`
        *   `pipeline_scout.py`: `PipelineScoutAgent` implementation.
        *   `configurator.py`: `ConfiguratorAgent` implementation.
        *   `blueprint_architect.py`: `BlueprintArchitectAgent` implementation.
        *   `deployment_engineer.py`: `DeploymentEngineerAgent` implementation.
    *   `tools/`: Directory for custom ADK tools.
        *   `__init__.py`
        *   `nf_core_tools.py`: Custom tools for nf-core interaction.
        *   `nextflow_tools.py`: Custom tools for Nextflow configuration file generation.
        *   `terraform_tools.py`: Custom tools for Terraform blueprint generation and execution.
        *   `deployment_workflow.py`: Wrapper around `SequentialAgent` for the deployment process.
    *   `requirements.txt`: Lists Python dependencies (adk-python, requests, etc.).
    *   `.env`: Example file for environment variables (e.g., GCP credentials path, default region).

**Implementation Notes:**

*   **LLM Integration:** Carefully design the prompts for each `LlmAgent` to guide their reasoning and tool usage effectively.
*   **Tool Interfaces:** Ensure that the input and output specifications (`_get_declaration`) of custom tools are precise and align with the data flow between agents.
*   **Asynchronous Operations:** Leverage the `run_async` method in custom tools for operations that might take time (like `terraform apply`).
*   **Human-in-the-Loop Placement:** Strategically place `get_user_choice_tool` calls or custom validation tools at points where human input or approval is critical (e.g., after pipeline selection, before significant cloud resource provisioning).

**5. Future Work (Beyond Initial Scope)**

*   **Pipeline Execution Agent:** An agent to trigger and monitor the Nextflow job on the provisioned cluster.
*   **Results Analysis Agent:** An agent to parse and summarize the outputs of the Nextflow pipeline.
*   **Cost Monitoring Agent:** An agent to track the cost of the cloud infrastructure.
*   **Support for Other Cloud Providers:** Extend `BlueprintArchitectAgent` and `DeploymentEngineerAgent` to support AWS, Azure, etc.
*   **Support for Other Workflow Managers:** Add agents for Cromwell, Snakemake, etc.
*   **More Sophisticated Resource Estimation:** Integrate with cloud provider APIs or use machine learning models for more accurate resource estimation.
*   **Workflow Persistence and Resumption:** Implement mechanisms to save and restore the state of the workflow.

**6. Conclusion**

This document provides a detailed plan for developing the `agentic_genomics` multi-agent system. By following this design and leveraging the Google ADK, we can build a robust and intelligent system to automate genomic analysis workflows on the cloud. The agentic approach offers significant benefits in terms of modularity, flexibility, and the potential for incorporating more advanced AI capabilities in the future.

https://deepwiki.com/google/adk-python/4-development-workflow
https://google.github.io/adk-docs/agents/multi-agents/
https://deepwiki.com/google/adk-python/5-deployment
https://google.github.io/adk-docs/agents/ 
https://google.github.io/adk-docs/agents/multi-agents/
https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/
https://google.github.io/adk-docs/api-reference/python/

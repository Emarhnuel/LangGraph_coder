# LangGraph Coder Crew

Welcome to the LangGraph Coder Crew project, powered by [CrewAI](https://crewai.com) and [LangGraph](https://langchain-ai.github.io/langgraph/). This project leverages a team of specialized AI agents to automate the process of building LangGraph applications. It takes a user-defined agent type, researches relevant LangGraph documentation (including text and images), plans the agent's conceptual design, and finally generates the Python code for the LangGraph application.

## Overview

The LangGraph Coder Crew streamlines the development of LangGraph agents by:

1.  **Processing Documentation:** An agent crawls specified LangGraph documentation pages, extracting key concepts, code examples, and architectural patterns from both text and visual elements (diagrams).
2.  **Planning Concepts:** Based on the user's desired agent type and the extracted knowledge, a planning agent determines the most suitable LangGraph components and patterns for the implementation. This plan requires user approval.
3.  **Generating Code:** A coding agent takes the approved plan and the processed documentation to write, test, and save the Python code for the specified LangGraph agent.

## How it Works

The project uses a CrewAI flow orchestrated in `src/coder_ai/main.py`. When run, it prompts the user for the type of LangGraph agent they wish to build. This input triggers the `LangGraphCoderCrew` defined in `src/coder_ai/crews/Crewai-langGraph/crew.py`.

### The Crew

The crew consists of three specialized agents defined in `src/coder_ai/crews/Crewai-langGraph/config/agents.yaml`:

1.  **`documentation_processor`**:
    *   **Goal:** Extract comprehensive information (text & visuals) from LangGraph documentation URLs and generate structured markdown files.
    *   **Tools:** `DocumentationCrawlerTool` (a custom tool using `crawl4ai`).
    *   **LLM:** Configured to use a multimodal model (e.g., Claude 3.7 Sonnet via OpenRouter).
2.  **`langgraph_concept_planner`**:
    *   **Goal:** Analyze user requirements and the processed documentation to propose the best LangGraph concepts/patterns.
    *   **Tools:** `SerperDevTool` for additional web searching if needed.
    *   **LLM:** Configured to use a capable reasoning model (e.g., DeepSeek-R1 via OpenRouter).
    *   **Interaction:** Requires human input to approve the proposed plan.
3.  **`langgraph_coder`**:
    *   **Goal:** Design, implement, and verify efficient LangGraph code based on the plan.
    *   **Tools:** `FileWriterTool` to save the generated code.
    *   **LLM:** Configured to use a strong coding model (e.g., Gemini 2.5 Pro via OpenRouter).
    *   **Capabilities:** `allow_code_execution` is enabled for potential code verification steps.

### The Tasks

The agents collaborate on tasks defined in `src/coder_ai/crews/Crewai-langGraph/config/tasks.yaml`:

1.  **`process_documentation`**: Crawls a predefined list of LangGraph documentation URLs.
2.  **`plan_langgraph_concepts`**: Develops the implementation plan based on the crawled docs and user's agent type.
3.  **`generate_code`**: Writes the LangGraph Python code according to the approved plan.

### Output

*   Processed documentation (Markdown files) is saved within the `knowledge/{agent_type}/` directory (created dynamically based on user input).
*   Generated Python code is saved in the `generated_code/{agent_type}/` directory (e.g., `generated_code/sports_betting/agent_implementation.py`).
*   A summary of the process, including file paths and any errors, is displayed at the end.

## Getting Started

### Prerequisites

*   Python >= 3.10 < 3.13
*   [UV](https://docs.astral.sh/uv/) (Python package manager)
*   API Keys for required services (see `.env` configuration)

### Installation

1.  **Install UV:**
    ```bash
    pip install uv
    ```

2.  **Install Project Dependencies:**
    Navigate to the project's root directory (`coder_ai`) and run:
    ```bash
    crewai install
    ```
    This uses `uv` to install dependencies listed in `pyproject.toml`, including `crewai`, `langgraph`, `python-dotenv`, etc.

3.  **Install Custom Tool Dependency:**
    The `DocumentationCrawlerTool` requires the `crawl4ai` library. Install it manually:
    ```bash
    pip install crawl4ai
    ```
    *(Note: Consider adding `crawl4ai` to your `pyproject.toml` dependencies for `crewai install` to handle it automatically)*

### Configuration

1.  **Create `.env` file:**
    If it doesn't exist, create a `.env` file in the `coder_ai` root directory.

2.  **Add API Keys:**
    Add the following required API keys to your `.env` file:
    ```dotenv
    OPENROUTER_API_KEY="your_openrouter_api_key"
    SERPER_API_KEY="your_serper_api_key"
    # Add any other keys required by the LLMs or tools you configure
    ```
    *   You need an OpenRouter key as the LLMs are configured via `openrouter.ai`.
    *   You need a Serper API key for the `langgraph_concept_planner`'s search tool.

## Running the Project

To run the LangGraph Coder flow, execute the following command from the `coder_ai` root directory:

```bash
crewai flow kickoff
```

This will start the process:

1.  You will be prompted to enter the type of AI agent you want to build (e.g., "customer support chatbot", "financial analyst").
2.  The `documentation_processor` agent will crawl the LangGraph docs.
3.  The `langgraph_concept_planner` will propose a plan. You will need to review and type 'yes' (or similar confirmation) in the terminal to approve it.
4.  The `langgraph_coder` agent will generate the code based on the approved plan.
5.  The results, including paths to generated knowledge and code files, will be printed.

You can also visualize the flow structure:

```bash
crewai flow plot
```

## Customization

*   **Agents:** Modify roles, goals, backstories, LLMs, or tools in `src/coder_ai/crews/Crewai-langGraph/config/agents.yaml`.
*   **Tasks:** Adjust task descriptions, expected outputs, assigned agents, or the list of documentation URLs in `src/coder_ai/crews/Crewai-langGraph/config/tasks.yaml`.
*   **Crew Logic:** Add or modify tools, change LLM configurations, adjust the crew process (e.g., `Process.hierarchical`), or alter the `@before_kickoff` logic in `src/coder_ai/crews/Crewai-langGraph/crew.py`.
*   **Flow & State:** Modify the overall application flow, user interaction, or the `LangGraphCoderState` model in `src/coder_ai/main.py`.
*   **Tools:** Enhance the `DocumentationCrawlerTool` or add new custom tools in the `src/coder_ai/tools/` directory.

## Support

For support, questions, or feedback regarding CrewAI:

*   Visit the [CrewAI documentation](https://docs.crewai.com)
*   Check the [GitHub repository](https://github.com/joaomdmoura/crewai)
*   [Join the Discord community](https://discord.com/invite/X4JWnZnxPb)
*   [Chat with the docs bot](https://chatg.pt/DWjSBZn)

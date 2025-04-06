#!/usr/bin/env python
from crewai import Agent, Task, Crew, Process
from crewai.project import agent, task, crew, before_kickoff, CrewBase
from crewai.llm import LLM
from coder_ai.tools.crawl4ai_tool import DocumentationCrawlerTool
from crewai_tools import FileWriterTool, SerperDevTool, FileReadTool
from crewai.memory import LongTermMemory
from crewai.memory.storage import ltm_sqlite_storage

# Import tools
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API keys from environment
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

llm = LLM(
    model="openrouter/google/gemini-2.5-pro-exp-03-25:free",
    base_url="https://openrouter.ai/api/v1",
    temperature=0.2,
    max_tokens=50000,
    api_key=OPENROUTER_API_KEY
)

llm1 = LLM(
    model="openrouter/deepseek/deepseek-r1",
    base_url="https://openrouter.ai/api/v1",
    temperature=0.2,
    api_key=OPENROUTER_API_KEY
)

llm2 = LLM(
    model="openrouter/anthropic/claude-3.7-sonnet:thinking",
    base_url="https://openrouter.ai/api/v1",
    temperature=0.2,
    api_key=OPENROUTER_API_KEY
)


llm3 = LLM(
    model="sambanova/DeepSeek-R1-Distill-Llama-70B",
    temperature=0.2
)


@CrewBase
class LangGraphCoderCrew:
    """LangGraph Coder Crew
    
    This crew automates the process of learning, planning, and implementing LangGraph-based agents.
    It extracts information from documentation and then uses that knowledge to plan 
    and implement custom LangGraph agents based on user requirements.
    """

    # YAML configuration files for agents and tasks
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    
    # Directory where generated code will be stored
    code_output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../generated_code"))
    
    # Initialize tools
    def __init__(self):
        # Create code output directory if it doesn't exist
        os.makedirs(self.code_output_dir, exist_ok=True)
        
        Path("memory").mkdir(exist_ok=True, parents=True)    
    
    @before_kickoff
    def prepare_inputs(self, inputs):
        """Prepare inputs before crew execution"""
        # Add code output directory path to inputs if not already present
        if 'code_output_dir' not in inputs:
            inputs['code_output_dir'] = self.code_output_dir
        
        # Create agent-specific output directory
        if 'agent_type' in inputs and inputs['agent_type']:
            agent_type = inputs['agent_type'].lower().replace(' ', '_')
            agent_code_dir = os.path.join(self.code_output_dir, agent_type)
            os.makedirs(agent_code_dir, exist_ok=True)
            inputs['agent_code_dir'] = agent_code_dir
        
        print(f"Code output directory: {self.code_output_dir}")
        return inputs
    
    
    # Define all agents from agents.yaml
    @agent
    def documentation_processor(self) -> Agent:
        return Agent(
            config=self.agents_config["documentation_processor"],
            verbose=True,
            multimodal=True,
            max_rpm=16,
            max_iter=12,
            llm=llm2,
            tools=[
                DocumentationCrawlerTool()
            ]
        )
    
    @agent
    def langgraph_concept_planner(self) -> Agent:
        return Agent(
            config=self.agents_config["langgraph_concept_planner"],
            verbose=True,
            max_rpm=10,
            llm=llm1,
            max_iter=6,
            tools=[
                SerperDevTool(
                    search_url="https://google.serper.dev/search",
                    n_results=8,
                    
                )
            ]
        )
    
    @agent
    def langgraph_coder(self) -> Agent:
        return Agent(
            config=self.agents_config["langgraph_coder"],
            verbose=True,
            max_rpm=20,
            llm=llm, 
            max_iter=8,
            allow_code_execution=True,
            tools=[
                FileWriterTool()
            ]
        )
    

    
    # Define all tasks from tasks.yaml
    @task
    def process_documentation(self) -> Task:
        return Task(
            config=self.tasks_config["process_documentation"],
            agent=self.documentation_processor(),
        )
    
    @task
    def plan_langgraph_concepts(self) -> Task:
        return Task(
            config=self.tasks_config["plan_langgraph_concepts"],
            agent=self.langgraph_concept_planner(),
        )
    
    @task
    def generate_code(self) -> Task:
        return Task(
            config=self.tasks_config["generate_code"],
            agent=self.langgraph_coder(),
            output_file="{agent_code_dir}/agent_implementation.py",
            create_directory=True
        )
    
    @crew
    def crew(self) -> Crew:
        """Creates the LangGraph Coder Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=True,
            planning=True,
            process=Process.sequential,
            long_term_memory=LongTermMemory(
                storage=ltm_sqlite_storage.LTMSQLiteStorage(
                    db_path="memory/audience_memory.db"
                )
            )
        )

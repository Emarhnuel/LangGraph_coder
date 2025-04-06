#!/usr/bin/env python
from typing import Optional, Dict, Any, List
import os
import sys
from pathlib import Path

from pydantic import BaseModel, Field
from dotenv import load_dotenv

from crewai.flow import Flow, listen, start

# Load environment variables
load_dotenv()

# Handle import of module with hyphen in name
crew_path = Path(__file__).parent / 'crews' / 'Crewai-langGraph'
sys.path.append(str(crew_path))

# Now import directly from the crew module
from crew import LangGraphCoderCrew


class LangGraphCoderState(BaseModel):
    """State model for the LangGraph Coder Flow."""
    
    # Basic information
    agent_type: str = ""  # Type of AI agent to build (e.g., "sports betting", "social media")
    
    # Knowledge management
    knowledge_base: Optional[str] = None  # Path to generated knowledge base
    knowledge_files: List[str] = Field(default_factory=list)  # List of knowledge files generated
    
    # Code generation
    generated_code: Optional[str] = None  # Path to generated code
    code_files: Dict[str, str] = Field(default_factory=dict)  # Mapping of file names to file paths
    code_output_dir: Optional[str] = None  # Directory where code files are stored
    
    # Execution results
    execution_results: Optional[str] = None  # Results from code execution
    execution_status: Optional[bool] = None  # Whether execution was successful
    
    # Additional metadata
    errors: List[str] = Field(default_factory=list)  # Any errors encountered during the process
    completion_percentage: float = 0.0  # Progress indicator


class LangGraphCoderFlow(Flow[LangGraphCoderState]):

    @start()
    def get_agent_type(self):
        """Get the type of AI agent to build with LangGraph."""
        print("\n=== LangGraph Coder ===\n")
        self.state.agent_type = input("What type of AI agent would you like to build with LangGraph? (e.g., sports betting, social media, etc.): ")
        self.state.completion_percentage = 10.0
        return self.state.agent_type

    @listen(get_agent_type)
    def generate_langgraph_agent(self, agent_type):
        """Generate a LangGraph agent based on the specified type."""
        print(f"\nGenerating a {self.state.agent_type} AI agent using LangGraph...")
        self.state.completion_percentage = 20.0
        
        # Create and launch the LangGraphCoderCrew with the appropriate input
        langgraph_crew = LangGraphCoderCrew()
        
        # Prepare the crew by setting up knowledge directories
        result = langgraph_crew.crew().kickoff(
            inputs={"agent_type": self.state.agent_type}
        )
        
        # Update the state with results from the crew
        self.state.completion_percentage = 90.0
        print("\nProcessing complete!")
        
        # Store the results in our structured state
        if hasattr(result, 'knowledge_base'):
            self.state.knowledge_base = result.knowledge_base
            
        if hasattr(result, 'knowledge_files') and isinstance(result.knowledge_files, list):
            self.state.knowledge_files = result.knowledge_files
        
        # Handle code output directory    
        if hasattr(result, 'code_output_dir'):
            self.state.code_output_dir = result.code_output_dir
        elif hasattr(result, 'agent_code_dir'):
            self.state.code_output_dir = result.agent_code_dir
            
        # If we have a code output directory, scan it for files
        if self.state.code_output_dir and os.path.exists(self.state.code_output_dir):
            # First, check for specific code files if they're provided
            if hasattr(result, 'code_files') and isinstance(result.code_files, dict):
                self.state.code_files = result.code_files
            else:
                # Otherwise scan the directory for Python files
                self.state.code_files = {}
                for root, _, files in os.walk(self.state.code_output_dir):
                    for file in files:
                        if file.endswith('.py'):
                            file_path = os.path.join(root, file)
                            relative_path = os.path.relpath(file_path, self.state.code_output_dir)
                            self.state.code_files[relative_path] = file_path
        
        # Store any explicitly provided generated code path
        if hasattr(result, 'generated_code'):
            self.state.generated_code = result.generated_code
            
        if hasattr(result, 'execution_results'):
            self.state.execution_results = result.execution_results
            
        if hasattr(result, 'execution_status'):
            self.state.execution_status = result.execution_status
            
        if hasattr(result, 'errors') and isinstance(result.errors, list):
            self.state.errors = result.errors
        
        self.state.completion_percentage = 100.0
        return result.raw

    @listen(generate_langgraph_agent)
    def display_results(self, crew_result):
        """Display the final results."""
        print("\n=== Results ===\n")
        print(f"AI Agent Type: {self.state.agent_type}")
        
        if self.state.knowledge_base:
            print(f"Knowledge Base: {self.state.knowledge_base}")
            
        if self.state.knowledge_files:
            print(f"Knowledge Files: {len(self.state.knowledge_files)} file(s) generated")
            for file in self.state.knowledge_files:
                print(f"  - {file}")
        
        # Display code output directory
        if self.state.code_output_dir:
            print(f"\nCode Output Directory: {self.state.code_output_dir}")
        
        # Display generated code information
        if self.state.generated_code:
            print(f"Generated Code: {self.state.generated_code}")
            
        if self.state.code_files:
            print(f"Code Files: {len(self.state.code_files)} file(s) generated")
            for name, path in self.state.code_files.items():
                print(f"  - {name}: {path}")
        
        # Display additional information    
        if self.state.execution_results:
            print(f"\nExecution Results: {self.state.execution_results}")
            
        if self.state.execution_status is not None:
            status = "Success" if self.state.execution_status else "Failed"
            print(f"Execution Status: {status}")
            
        if self.state.errors:
            print(f"Errors: {len(self.state.errors)} error(s) encountered")
            for error in self.state.errors:
                print(f"  - {error}")
                
        print(f"\nCompletion: {self.state.completion_percentage}%")
        
        return "Flow completed successfully"


def kickoff():
    """Launch the LangGraph Coder Flow."""
    coder_flow = LangGraphCoderFlow()
    result = coder_flow.kickoff()
    return result


def plot():
    """Generate a visualization of the LangGraph Coder Flow."""
    coder_flow = LangGraphCoderFlow()
    coder_flow.plot()


if __name__ == "__main__":
    kickoff()

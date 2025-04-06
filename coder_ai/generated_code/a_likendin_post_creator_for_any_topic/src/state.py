# src/state.py
from typing import TypedDict, List, Optional, Union
from langchain_core.messages import AIMessage, HumanMessage

class PostCreatorState(TypedDict):
    """
    Represents the state of the LinkedIn post creation workflow.
    """
    # Input requirements
    topic: str
    audience: str
    tone: str
    keywords: List[str]
    length: str  # "short", "medium", "long"

    # Working memory
    research_notes: List[str]
    draft_versions: List[str]
    current_draft: str

    # Messaging (Optional, could be used for more complex interactions)
    # messages: List[Union[HumanMessage, AIMessage]]

    # Feedback
    feedback: List[str] # List of feedback strings

    # Status tracking
    status: str  # e.g., "researching", "drafting", "refining", "adding_hashtags", "finalizing", "complete", "error"

    # Error info
    error_message: Optional[str]

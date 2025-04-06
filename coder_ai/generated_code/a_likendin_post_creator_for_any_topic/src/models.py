from typing import TypedDict, List, Optional, Union
from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

class PostCreatorState(TypedDict):
    """Represents the state of the LinkedIn post creation workflow."""

    # Input requirements
    topic: str
    audience: str
    tone: str
    keywords: List[str]
    length: str  # e.g., "short", "medium", "long"

    # Working memory
    research_notes: List[str] = Field(default_factory=list)
    draft_versions: List[str] = Field(default_factory=list)
    current_draft: Optional[str] = None
    hashtags: List[str] = Field(default_factory=list)

    # Messaging (optional, for more complex interaction)
    messages: List[Union[HumanMessage, AIMessage]] = Field(default_factory=list)

    # Feedback
    feedback: List[str] = Field(default_factory=list)
    needs_revision: bool = False # Flag to trigger revision loop

    # Status tracking
    status: str = "idle"  # e.g., "idle", "researching", "drafting", "refining", "adding_hashtags", "finalizing", "complete", "error"
    error_message: Optional[str] = None

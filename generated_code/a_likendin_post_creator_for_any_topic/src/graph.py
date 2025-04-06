from langgraph.graph import StateGraph, END
from .models import PostCreatorState
from .nodes import (
    research_topic,
    create_initial_draft,
    review_and_refine,
    add_hashtags,
    finalize_post
)
import logging

logger = logging.getLogger(__name__)

# --- Conditional Edge Logic ---

def should_refine(state: PostCreatorState) -> str:
    """Determines if the draft needs refinement based on the 'needs_revision' flag."""
    logger.info(f"Checking if refinement is needed. Needs revision: {state.get('needs_revision', False)}")
    if state.get('error_message'):
        logger.warning("Error detected, ending workflow.")
        return "__end__" # End if any node reported an error
    if state.get('needs_revision', False):
        logger.info("Routing to: review_and_refine")
        return "review_and_refine" # Go back to refine if revision is requested
    else:
        logger.info("Routing to: add_hashtags")
        return "add_hashtags" # Proceed if no revision needed

def check_for_errors(state: PostCreatorState) -> str:
    """Checks if an error occurred in the previous step."""
    if state.get('error_message'):
        logger.error(f"Workflow halted due to error: {state['error_message']}")
        return "__end__"
    logger.debug("No errors detected, proceeding.")
    # Determine next step based on current status if no error
    status = state.get('status')
    if status == 'drafting':
        return 'create_initial_draft'
    elif status == 'awaiting_review':
         # This is the point where external input (feedback/revision request) would be integrated.
         # For this simulation, we go directly to the check.
        return 'check_revision_needed'
    elif status == 'adding_hashtags':
        return 'add_hashtags'
    elif status == 'finalizing':
        return 'finalize_post'
    else:
        logger.warning(f"Unknown status for routing: {status}. Ending.")
        return "__end__"

# --- Graph Definition ---

def create_linkedin_post_graph() -> StateGraph:
    """Creates and configures the LangGraph StateGraph for LinkedIn post creation."""
    workflow = StateGraph(PostCreatorState)

    # Add nodes
    logger.info("Adding nodes to the graph...")
    workflow.add_node("research", research_topic)
    workflow.add_node("create_initial_draft", create_initial_draft)
    workflow.add_node("review_and_refine", review_and_refine)
    workflow.add_node("add_hashtags", add_hashtags)
    workflow.add_node("finalize_post", finalize_post)

    # Set entry point
    workflow.set_entry_point("research")

    # Add edges with error checking
    logger.info("Adding edges to the graph...")
    workflow.add_conditional_edges(
        "research",
        check_for_errors,
        {
            "create_initial_draft": "create_initial_draft",
            "__end__": END
        }
    )
    workflow.add_conditional_edges(
        "create_initial_draft",
        check_for_errors,
        {
            # After drafting, always go to the revision check point
            "check_revision_needed": "check_revision_needed",
            "__end__": END
        }
    )

    # Conditional edge after drafting to decide if refinement is needed
    # This node acts as the decision point based on external input (simulated via 'needs_revision' flag)
    workflow.add_conditional_edges(
        "check_revision_needed", # A conceptual node name for the decision point
        should_refine, # The function that checks the 'needs_revision' flag
        {
            "review_and_refine": "review_and_refine", # If needs_revision is True
            "add_hashtags": "add_hashtags",      # If needs_revision is False
            "__end__": END # Handle potential error state from should_refine itself (though unlikely here)
        }
    )

    # Edge from refinement back to the revision check (or forward if done)
    workflow.add_conditional_edges(
        "review_and_refine",
        check_for_errors, # Check for errors after refinement attempt
        {
            "adding_hashtags": "add_hashtags", # If refinement successful and no more revisions needed
            "__end__": END # If refinement failed
        }
    )

    workflow.add_conditional_edges(
        "add_hashtags",
        check_for_errors,
        {
            "finalize_post": "finalize_post",
            "__end__": END
        }
    )

    # Final edge to END
    workflow.add_edge("finalize_post", END)

    logger.info("Graph definition complete.")
    return workflow

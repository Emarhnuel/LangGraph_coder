import time
import random
import logging
from typing import Dict, Any
from .models import PostCreatorState

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Node Functions ---

def research_topic(state: PostCreatorState) -> Dict[str, Any]:
    """Simulates researching the topic based on input."""
    logger.info(f"Researching topic: {state['topic']} for audience: {state['audience']}")
    state['status'] = "researching"
    try:
        # Simulate API call or complex logic
        time.sleep(1)
        if random.random() < 0.05: # Simulate occasional research failure
            raise ValueError("Failed to gather sufficient research data.")

        research_notes = [
            f"Key insight about {state['topic']} relevant to {state['audience']}.",
            f"Statistic: 75% of {state['audience']} are interested in {state['keywords'][0] if state['keywords'] else 'this topic'}.",
            f"Emerging trend: {state['topic']} is evolving rapidly."
        ]
        logger.info("Research complete.")
        return {"research_notes": research_notes, "status": "drafting", "error_message": None}
    except Exception as e:
        logger.error(f"Error during research: {e}")
        return {"status": "error", "error_message": f"Research failed: {str(e)}"}

def create_initial_draft(state: PostCreatorState) -> Dict[str, Any]:
    """Simulates creating an initial draft based on research and requirements."""
    logger.info("Creating initial draft...")
    state['status'] = "drafting"
    try:
        if not state.get('research_notes'):
            raise ValueError("Cannot create draft without research notes.")

        # Simulate LLM call
        time.sleep(1.5)
        draft = f"**Draft 1: {state['topic']} for {state['audience']}**\n\n" \
                f"Tone: {state['tone']}. Length: {state['length']}. Keywords: {', '.join(state['keywords'])}.\n\n" \
                f"Based on research: {state['research_notes'][0]}... #InitialDraft"

        if random.random() < 0.05: # Simulate occasional drafting failure
            raise ValueError("LLM failed to generate coherent draft.")

        logger.info("Initial draft created.")
        current_versions = state.get('draft_versions', [])
        return {
            "current_draft": draft,
            "draft_versions": current_versions + [draft],
            "status": "awaiting_review", # Changed status to wait for review decision
            "error_message": None
        }
    except Exception as e:
        logger.error(f"Error during drafting: {e}")
        return {"status": "error", "error_message": f"Drafting failed: {str(e)}"}

def review_and_refine(state: PostCreatorState) -> Dict[str, Any]:
    """Simulates refining the post based on feedback (if any)."""
    logger.info("Reviewing and potentially refining draft...")
    state['status'] = "refining"
    try:
        current_draft = state.get('current_draft')
        if not current_draft:
            raise ValueError("No draft available to refine.")

        feedback = state.get('feedback', [])
        needs_revision = state.get('needs_revision', False)

        if not needs_revision or not feedback:
            logger.info("No revisions requested or no feedback provided. Proceeding.")
            # Reset feedback and revision flag for next potential loop
            return {"status": "adding_hashtags", "feedback": [], "needs_revision": False, "error_message": None}

        logger.info(f"Refining draft based on feedback: {feedback}")
        # Simulate LLM call for refinement
        time.sleep(1)
        refined_draft = f"{current_draft}\n\n**Refinement based on feedback:** {' '.join(feedback)} #Refined"

        if random.random() < 0.05: # Simulate occasional refinement failure
            raise ValueError("LLM failed to refine draft based on feedback.")

        logger.info("Draft refined.")
        current_versions = state.get('draft_versions', [])
        # Reset feedback and revision flag after successful refinement
        return {
            "current_draft": refined_draft,
            "draft_versions": current_versions + [refined_draft],
            "status": "adding_hashtags",
            "feedback": [],
            "needs_revision": False,
            "error_message": None
        }
    except Exception as e:
        logger.error(f"Error during refinement: {e}")
        return {"status": "error", "error_message": f"Refinement failed: {str(e)}"}

def add_hashtags(state: PostCreatorState) -> Dict[str, Any]:
    """Simulates adding relevant hashtags to the post."""
    logger.info("Adding hashtags...")
    state['status'] = "adding_hashtags"
    try:
        current_draft = state.get('current_draft')
        if not current_draft:
            raise ValueError("No draft available to add hashtags to.")

        # Simulate LLM call or logic for hashtag generation
        time.sleep(0.5)
        hashtags = [f"#{kw.replace(' ', '')}" for kw in state['keywords']] + [f"#{state['topic'].replace(' ', '')}", "#LinkedInTips"]

        if random.random() < 0.02: # Simulate rare hashtag failure
             raise ValueError("Failed to generate relevant hashtags.")

        logger.info(f"Hashtags generated: {hashtags}")
        # Append hashtags to the current draft (or store separately)
        # Here we store them separately in the state
        return {"hashtags": hashtags, "status": "finalizing", "error_message": None}
    except Exception as e:
        logger.error(f"Error adding hashtags: {e}")
        return {"status": "error", "error_message": f"Hashtag generation failed: {str(e)}"}

def finalize_post(state: PostCreatorState) -> Dict[str, Any]:
    """Simulates final checks and formatting."""
    logger.info("Finalizing post...")
    state['status'] = "finalizing"
    try:
        current_draft = state.get('current_draft')
        hashtags = state.get('hashtags', [])
        if not current_draft:
            raise ValueError("No draft available to finalize.")

        # Simulate final review/formatting
        time.sleep(0.5)
        final_post = f"**Final LinkedIn Post**\n\n{current_draft}\n\n{' '.join(hashtags)}"

        logger.info("Post finalized.")
        current_versions = state.get('draft_versions', [])
        return {
            "current_draft": final_post,
            "draft_versions": current_versions + [final_post],
            "status": "complete",
            "error_message": None
        }
    except Exception as e:
        logger.error(f"Error finalizing post: {e}")
        return {"status": "error", "error_message": f"Finalization failed: {str(e)}"}

import argparse
import logging
from pprint import pprint
from src.graph import create_linkedin_post_graph
from src.models import PostCreatorState

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_post_creator(topic: str, audience: str, tone: str, keywords: list[str], length: str, needs_revision: bool = False, feedback: list[str] = None):
    """Runs the LinkedIn post creator workflow."""
    logger.info("Initializing LinkedIn Post Creator Graph...")
    app = create_linkedin_post_graph().compile()
    logger.info("Graph compiled successfully.")

    # Initial state
    initial_state: PostCreatorState = {
        "topic": topic,
        "audience": audience,
        "tone": tone,
        "keywords": keywords,
        "length": length,
        "research_notes": [],
        "draft_versions": [],
        "current_draft": None,
        "hashtags": [],
        "messages": [],
        "feedback": feedback if feedback else [],
        "needs_revision": needs_revision, # Set based on input
        "status": "idle",
        "error_message": None
    }

    logger.info(f"Starting workflow with initial state:")
    pprint(initial_state)

    # Run the workflow
    # Use stream to see intermediate states (optional but good for debugging)
    final_state = None
    for output in app.stream(initial_state):
        # stream() yields dictionaries with node names as keys
        for key, value in output.items():
            logger.info(f"--- Output from node: {key} ---")
            pprint(value)
            final_state = value # Keep track of the latest full state

    logger.info("--- Workflow Finished ---")
    if final_state:
        logger.info(f"Final Status: {final_state.get('status')}")
        if final_state.get('error_message'):
            logger.error(f"Error: {final_state['error_message']}")
        else:
            logger.info("Final Post Draft:")
            print("\n================ FINAL POST ================")
            print(final_state.get('current_draft', 'No final draft generated.'))
            print("==========================================\n")
            # logger.info("Draft History:")
            # pprint(final_state.get('draft_versions', []))
    else:
        logger.error("Workflow did not produce a final state.")

    return final_state

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the LinkedIn Post Creator AI Agent.")
    parser.add_argument("--topic", type=str, default="AI in Marketing", help="The topic for the LinkedIn post.")
    parser.add_argument("--audience", type=str, default="Marketing Professionals", help="The target audience.")
    parser.add_argument("--tone", type=str, default="Informative", help="The desired tone (e.g., Informative, Casual, Formal).")
    parser.add_argument("--keywords", nargs='+', default=["AI", "MarketingAutomation", "ContentCreation"], help="List of keywords.")
    parser.add_argument("--length", type=str, default="medium", choices=["short", "medium", "long"], help="Desired post length.")
    parser.add_argument("--needs-revision", action='store_true', help="Flag to simulate a revision request after the first draft.")
    parser.add_argument("--feedback", nargs='+', default=["Make it more engaging.", "Add a call to action."], help="Simulated feedback for revision.")

    args = parser.parse_args()

    # Example run without revision request
    print("\n--- Running Workflow (No Revision Requested) ---")
    run_post_creator(
        topic=args.topic,
        audience=args.audience,
        tone=args.tone,
        keywords=args.keywords,
        length=args.length,
        needs_revision=False
    )

    # Example run WITH revision request
    print("\n--- Running Workflow (Revision Requested) ---")
    run_post_creator(
        topic=args.topic,
        audience=args.audience,
        tone=args.tone,
        keywords=args.keywords,
        length=args.length,
        needs_revision=True,
        feedback=args.feedback
    )

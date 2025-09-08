# /home/ds/sambashare/GOB/GOB-V1.0/core_test/test_runner.py
from logger import get_logger
from state_manager import GOBStateManager

def main():
    logger = get_logger()
    logger.info("Logger import test: [SUCCESS]")
    logger.info("Grid Overwatch Bridge test harness is operational.")
    
    logger.info("Initiating isolated test of GOBStateManager...")

    try:
        state_manager = GOBStateManager()
        state = state_manager.get_state()
        
        logger.info("State Manager Instantiation Test: [SUCCESS]")
        logger.info(f"Initial state loaded successfully. Session ID: {state.get('session_id', 'N/A')}")
        
        # Log a snippet of the state for verification
        logger.debug(f"Full initial state dump: {state}")

    except Exception as e:
        logger.error("State Manager Instantiation Test: [FAILURE]", exc_info=True)
        logger.error(f"Encountered a critical error during state manager initialization: {e}")

if __name__ == "__main__":
    main()

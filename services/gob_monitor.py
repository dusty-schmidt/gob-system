# /home/ds/sambashare/GOB/services/gob_monitor.py
# Role: Real-time monitoring interface for Grid Overwatch Bridge service
# Displays live status updates and system state information via TUI

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, Any, Optional

# --- NEW: More verbose startup ---
print("--- GOB Monitor Initializing ---")
print(f"Python executable: {sys.executable}")
print(f"Script path: {__file__}")

# Add the project's 'utils' directory to the Python path
UTILS_PATH = Path(__file__).parent.parent.parent / 'utils'
sys.path.insert(0, str(UTILS_PATH))
print(f"Attempting to import 'logger' from: {UTILS_PATH}")

try:
    from logger import setup_logger
    from config import MONITOR_LOG_FILE, PORTS, BRIDGE_PORT_FILE
    print("--> Universal logger and config modules imported successfully.")
except ImportError as e:
    print(f"FATAL: Cannot import universal logger or config from {UTILS_PATH}.")
    print(f"--> Error: {e}")
    sys.exit(1)

# --- End of new startup section ---


class GOBMonitor:
    """Grid Overwatch Bridge monitoring interface."""

    def __init__(self, endpoint: str | None = None,
                 refresh_interval: int = 5):
        # Default endpoint from shared config; allow override by arg
        if endpoint is None:
            endpoint = f"http://localhost:{PORTS['grid_overwatch_bridge']}/state"
        self.endpoint = endpoint
        self.refresh_interval = refresh_interval
        # Note: Logger is now initialized in main() to ensure console output first
        self.logger = None
        self.running = False

    def set_logger(self, logger):
        """Assigns the logger instance."""
        self.logger = logger
        self.logger.info("Logger assigned to GOBMonitor instance.")

    def clear_screen(self) -> None:
        """Clear terminal screen across platforms."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def fetch_state(self) -> tuple[bool, Optional[Dict[Any, Any]], str]:
        """
        Fetch current state from GOB endpoint.

        Returns:
            tuple: (success, data, status_message)
        """
        try:
            with urllib.request.urlopen(self.endpoint, timeout=2) as response:
                if response.getcode() == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    return True, data, "ONLINE"
                else:
                    return False, None, f"HTTP {response.getcode()}"

        except urllib.error.URLError as e:
            # Optional enhancement: if the bridge persisted a different port, try once
            try:
                with open(BRIDGE_PORT_FILE, 'r') as pf:
                    port_str = pf.read().strip()
                if port_str and port_str.isdigit():
                    alt_endpoint = f"http://localhost:{int(port_str)}/state"
                    if alt_endpoint != self.endpoint:
                        self.logger.info(f"Retrying state fetch using discovered port: {alt_endpoint}")
                        self.endpoint = alt_endpoint
                        with urllib.request.urlopen(self.endpoint, timeout=2) as response:
                            if response.getcode() == 200:
                                data = json.loads(response.read().decode('utf-8'))
                                return True, data, "ONLINE"
            except Exception:
                pass
            return False, None, f"OFFLINE - {e.reason}"
        except json.JSONDecodeError:
            return False, None, "INVALID RESPONSE"
        except Exception as e:
            self.logger.error(f"Unhandled exception in fetch_state: {e}", exc_info=True)
            return False, None, f"ERROR - {str(e)}"

    def render_header(self) -> None:
        """Display monitor header."""
        print("=" * 65)
        print("GRID OVERWATCH BRIDGE - LIVE MONITOR")
        print("=" * 65)
        print(f"Endpoint: {self.endpoint}")
        print(f"Refresh:  {self.refresh_interval}s")
        print("-" * 65)

    def render_status(self, success: bool, status_msg: str) -> None:
        """Display connection status."""
        status_indicator = "✓" if success else "✗"
        print(f"STATUS: [{status_indicator}] {status_msg}")

    def render_data(self, data: Optional[Dict[Any, Any]]) -> None:
        """Display state data if available."""
        if data:
            print("\n--- SYSTEM STATE ---")
            print(json.dumps(data, indent=2, default=str))
        else:
            print("\n--- NO DATA AVAILABLE ---")

    def render_footer(self) -> None:
        """Display monitor footer."""
        print("\n" + "=" * 65)
        print(f"Next refresh in {self.refresh_interval}s (Ctrl+C to exit)")

    def display_cycle(self) -> None:
        """Execute one complete display cycle."""
        self.clear_screen()
        self.render_header()

        success, data, status_msg = self.fetch_state()
        self.render_status(success, status_msg)
        self.render_data(data)
        self.render_footer()

        if success:
            self.logger.debug(f"Successfully fetched state data")
        else:
            self.logger.warning(f"Failed to fetch state: {status_msg}")

    def start(self) -> None:
        """Start the monitoring loop."""
        self.logger.info("Starting GOB Monitor main loop...")
        self.running = True

        try:
            while self.running:
                self.display_cycle()
                time.sleep(self.refresh_interval)

        except KeyboardInterrupt:
            self.stop()

    def stop(self) -> None:
        """Stop the monitoring loop gracefully."""
        self.running = False
        print("\n\nShutdown signal received. Terminating monitor...")
        self.logger.info("GOB Monitor terminated by user")


def main() -> None:
    """Initialize and run the GOB monitor."""
    # Initialize the universal logger with a specific name for this component
    logger = setup_logger("gob-monitor", MONITOR_LOG_FILE)
    
    monitor = GOBMonitor()
    monitor.set_logger(logger)
    
    logger.info("Monitor will start in 3 seconds...")
    print("--> Monitor will take over the screen in 3 seconds. Press Ctrl+C to exit at any time.")
    time.sleep(3)
    
    monitor.start()


if __name__ == "__main__":
    main()

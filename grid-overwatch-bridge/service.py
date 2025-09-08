#!/usr/bin/env python3
"""
Grid Overwatch Bridge - Core Service
"""
import time
import signal
import threading
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

import sys
from pathlib import Path

# Add the project's 'lib' directory to the Python path
# This allows us to import the universal logger
LIB_PATH = Path(__file__).parent.parent / 'lib'
sys.path.insert(0, str(LIB_PATH))

try:
    from logger import setup_logger
    from state_manager import get_state_manager
except ImportError as e:
    print(f"FATAL: Could not import universal logger from {LIB_PATH}")
    print(f"Error: {e}")
    sys.exit(1)

# Global instances
logger = setup_logger("grid-overwatch-bridge")
state_manager = None
health_server = None


class HealthHandler(BaseHTTPRequestHandler):
    """HTTP handler for health checks and core state"""

    def do_GET(self):
        global state_manager
        client_ip = self.client_address[0]

        if self.path == '/health':
            logger.debug(f"Health check ping received from {client_ip}")
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = b'{"status": "healthy", "service": "grid-overwatch-bridge"}'
            self.wfile.write(response)

        elif self.path == '/state':
            logger.info(f"State request received from {client_ip}. Transmitting GOB core state.")
            try:
                if state_manager:
                    # Note: The original file had get_core_state(), which doesn't exist.
                    # Correcting to use get_state_for_ui() which is designed for this.
                    core_state = state_manager.get_state_for_ui()
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = json.dumps(core_state, indent=2).encode('utf-8')
                    self.wfile.write(response)
                else:
                    logger.warning(f"State request from {client_ip} failed: State manager not available.")
                    self.send_response(503)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = b'{"error": "State manager offline"}'
                    self.wfile.write(response)
            except Exception as e:
                logger.error(f"Critical error processing /state request from {client_ip}: {e}", exc_info=True)
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = json.dumps({"error": "Internal system failure"}).encode('utf-8')
                self.wfile.write(response)

        else:
            logger.warning(f"Invalid path request from {client_ip}: {self.path}")
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error": "Endpoint not found"}')

    def log_message(self, format, *args):
        """Redirect HTTP access logs to our cyberpunk logger."""
        logger.debug(f"HTTP request: {self.address_string()} {format % args}")


def start_health_server():
    """Start the health check HTTP server"""
    global health_server
    try:
        health_server = HTTPServer(('localhost', 8051), HealthHandler)
        logger.info("Health endpoint online. Listening on http://localhost:8051/health")
        logger.info("Core state endpoint online. Listening on http://localhost:8051/state")
        health_server.serve_forever()
    except Exception as e:
        logger.error(f"Fatal error: Failed to start health server: {e}", exc_info=True)


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    global state_manager, health_server
    
    logger.warning(f"Signal {signum} received. Initiating graceful shutdown sequence.")
    
    if health_server:
        logger.info("Shutting down HTTP server...")
        health_server.shutdown()
    
    # The original script had a stop_monitoring() method which doesn't exist.
    # We will just log that the state manager is shutting down.
    if state_manager:
        logger.info("State manager shutting down.")
    
    logger.info("Grid Overwatch Bridge offline.")
    sys.exit(0)


def main():
    """Main entry point"""
    global state_manager
    
    logger.info("Booting Grid Overwatch Bridge...")
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        logger.info("Starting health and state endpoint subroutine...")
        health_thread = threading.Thread(target=start_health_server, daemon=True)
        health_thread.start()
        
        logger.info("Initializing GOB State Manager...")
        state_manager = get_state_manager()
        # The original script had a start_monitoring() method which doesn't exist.
        # The state manager is already active upon instantiation.
        logger.info("State manager initialized successfully.")
        
        logger.info("Grid Overwatch Bridge is now fully operational.")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)
    except Exception as e:
        logger.error("A critical unhandled exception occurred in the main loop.", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

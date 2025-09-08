# Grid Overwatch Bridge (GOB) - Core Service

## Overview

The Grid Overwatch Bridge is the foundational "involuntary nervous system" for the GOB multi-agent framework. It is a lightweight, standalone service responsible for monitoring the core state of the system and providing that information to other components, such as the user interface.

This service is designed to be highly reliable and have minimal dependencies. It runs independently of the main GOB agent service.

## Core Components

-   `service.py`: The main entry point for the service. This script starts the lightweight HTTP server.
-   `state_manager.py`: The heart of the service. It is responsible for creating, maintaining, and providing the central `gob_state.json` file.
-   `logger.py`: A custom cyberpunk-themed logger for all core service output.

## How to Run

The Grid Overwatch Bridge is started using a dedicated shell script that ensures the correct environment is activated.

**To run in the foreground (for debugging):**
```bash
./start_gob_core.sh
```

**To run as a background service:**
```bash
./start_gob_core.sh &
```

## Endpoints

The service exposes a simple HTTP API on `http://localhost:8051`:

-   **/state**: Returns a JSON object with the complete, real-time state of the GOB system, including uptime and connection status. This is the primary endpoint for the frontend.
-   **/health**: Returns a simple `{"status": "healthy"}` response for health checks.

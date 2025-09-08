# Enhanced GOB Work Prompt

This guide defines the standard workflow for contributors. It consolidates existing conventions and adds guidance for modular code, TOML-based configuration, a centralized logger, and a conda environment.

1. Context Gathering
- Before starting, read the last few entries in /home/ds/sambashare/GOB/WATERCOOLER.md.
- Carry forward any relevant notes into your new pre-log.

2. Pre-Log the Plan
- Create a Markdown file in /home/ds/sambashare/GOB/work_logs/pre.
- Include:
  - Timestamp
  - Task description and objectives
  - Necessary steps
  - References to prior logs or watercooler notes
- Never use dummy information—request real credentials from the user if needed.

3. Execute the Work
- Complete the steps as planned.
- Follow the GOB system philosophy: clean, maintainable, robust.
- Remember: core services run on the host; agents run in Docker.
- Write modular code that logically makes sense.
- Use the centralized logger (utils/logger.py) for consistent logging.
- Use TOML-based configuration to avoid hardcoding values and to support overrides.

4. Post-Log the Results
- Save a document in /home/ds/sambashare/GOB/work_logs/post.
- Include:
  - Timestamp
  - What was done
  - Issues encountered
  - Next steps
  - If applicable, note why files were moved to scraps

5. File Hygiene
- Move unneeded created files into /home/ds/sambashare/GOB/work_logs/scraps.
- Document the reason in your post-log.

6. Watercooler Summary
- Append a new entry in /home/ds/sambashare/GOB/WATERCOOLER.md using the structured format:
  - What was done
  - What’s next
  - Notes/context from previous work

Configuration (TOML)
- Primary project-level config is stored in config/gob.toml.
- Prefer TOML keys with underscores to simplify usage in Python.
- Example load and fallback pattern:

```python
from pathlib import Path
import toml

# Load primary config
cfg_path = Path("config/gob.toml")
cfg = toml.load(cfg_path)

# Example access
ports = cfg.get("ports", {})
logs = cfg.get("logs", {})
```

Centralized Logger
- Always use utils/logger.py for consistent formatting and dual output (file + stdout).

```python
from utils.logger import setup_logger

logger = setup_logger("gob-example", "/home/ds/sambashare/GOB/GOB-system/logs/example.log")
logger.info("Component started")
```

Conda Environment
- Use the provided environment.yml to create/activate the development environment.

Commands:
- conda env create -f environment.yml
- conda activate gob
- pip install -r GOB-system/requirements.txt

MDC Component Documentation
- Each component should maintain a Component.mdc file with purpose, status, runbook, dependencies, and interfaces.
- Index and schema: GOB-system/COMPONENTS.mdc

References
- DEV-RULES.md
- WATERCOOLER.md
- work_logs/pre and work_logs/post
- GOB-system/COMPONENTS.mdc
``` 

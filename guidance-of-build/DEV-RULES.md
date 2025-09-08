# GOB Development Guidelines

This document outlines the standards and procedures for development within the GOB homelab system.
mar
See also: GOB-WORK-PROMPT.md for the step-by-step workflow, and GOB-system/COMPONENTS.mdc for component documentation conventions.

---

## 1. Context Gathering

* Always read the last few entries in `/home/ds/sambashare/GOB/WATERCOOLER.md` before starting any work.
* Extract and carry forward any relevant notes into your new pre-log.

## 2. Pre-Logging the Plan

* Create a Markdown file in `/home/ds/sambashare/GOB/work_logs/pre`.
* Include the following:

  * Timestamp of log creation
  * Task description and objectives
  * Step-by-step plan for execution
  * References to prior logs or watercooler notes
* Never use placeholder information; request real credentials from the user if required.

## 3. Executing Work

* Follow the planned steps carefully.
* Maintain the GOB system philosophy: clean, maintainable, robust.
* Remember:

  * Core services run on the host system.
  * Agents execute inside Docker containers.

Additional conventions:

* Modular code: keep components small and well-factored.
* Centralized logging: use utils/logger.py to emit logs (file + stdout).
* Configuration: prefer TOML at config/gob.toml; avoid hardcoding.
* Environment: use conda (environment.yml) for host development; pip install -r GOB-system/requirements.txt after activation.
* Component documentation: maintain Component.mdc per component; index in GOB-system/COMPONENTS.mdc.

## 4. Post-Logging Results

* Save a document in `/home/ds/sambashare/GOB/work_logs/post`.
* Include:

  * Timestamp
  * Description of what was done
  * Issues encountered
  * Next steps
  * If applicable, reasons why files were moved to scraps

## 5. File Hygiene

* Move unneeded or temporary files to `/home/ds/sambashare/GOB/work_logs/scraps`.
* Document the reason for each move in the post-log.

## 6. Watercooler Summary

* Append a new entry in `/home/ds/sambashare/GOB/WATERCOOLER.md`.
* Structured format:

  * What was done
  * What’s next
  * Notes and context from previous work

References and resources

* Workflow: GOB-WORK-PROMPT.md
* Component docs: GOB-system/COMPONENTS.mdc and Component.mdc files in each component directory
* Config: config/gob.toml (TOML)
* Logger: utils/logger.py
* Environment: environment.yml

---

By adhering to these guidelines, GOB developers ensure consistency, maintainability, and clear communication across the homelab projects.

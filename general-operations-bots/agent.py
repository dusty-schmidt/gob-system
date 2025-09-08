import asyncio, random, string, sys, os
import nest_asyncio

nest_asyncio.apply()

# Add the parent directory of 'general-operations-bots' to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Awaitable, Coroutine, Dict, Literal
from enum import Enum
import uuid
import models
import traceback

from python.helpers import extract_tools, files, errors, history, tokens
from python.helpers import dirty_json
from python.helpers.print_style import PrintStyle

from langchain_core.prompts import (
    ChatPromptTemplate,
)
from langchain_core.messages import SystemMessage, BaseMessage

import python.helpers.log as Log
from python.helpers.dirty_json import DirtyJson
from python.helpers.defer import DeferredTask
from typing import Callable
from python.helpers.localization import Localization
from python.helpers.extension import call_extensions
from python.helpers.errors import RepairableException

# Import the global logger
from lib.logger import setup_logger

# Initialize the logger for the agent module
logger = setup_logger('gob-agent')
# ... (rest of the file is the same)

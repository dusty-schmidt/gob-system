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

class AgentContextType(Enum):
    AGENT = "agent"
    USER = "user"

@dataclass
class UserMessage:
    content: str

@dataclass
class AgentContext:
    type: AgentContextType
    message: UserMessage

@dataclass
class LoopData:
    pass

class Agent:
    pass

@dataclass
class AgentConfig:
    chat_model: models.ModelConfig
    utility_model: models.ModelConfig
    embeddings_model: models.ModelConfig
    browser_model: models.ModelConfig
    profile: str = "default"
    memory_subdir: str = "default"
    knowledge_subdirs: list[str] = field(default_factory=lambda: ["default"])
    mcp_servers: str = ""
    browser_http_headers: str = ""
    code_exec_mode: str = "local"
    code_exec_env: str = "docker"
    ssh_user: str = "user"
    ssh_host: str = "localhost"
    ssh_port: int = 22
    ssh_pass: str = ""
    additional: dict = field(default_factory=dict)
# ... (rest of the file is the same)

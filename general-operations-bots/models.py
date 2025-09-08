import sys, os
from dataclasses import dataclass, field
from enum import Enum
import logging
from typing import (
    Any,
    Awaitable,
    Callable,
    List,
    Optional,
    Iterator,
    AsyncIterator,
    Tuple,
    TypedDict,
)
import traceback

# Add the parent directory of 'general-operations-bots' to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from litellm import completion, acompletion, embedding
import litellm

from python.helpers import dotenv
from python.helpers import settings
from python.helpers.dotenv import load_dotenv
from python.helpers.providers import get_provider_config
from python.helpers.rate_limiter import RateLimiter
from python.helpers.tokens import approximate_tokens

from langchain_core.language_models.chat_models import SimpleChatModel
from langchain_core.outputs.chat_generation import ChatGenerationChunk
from langchain_core.callbacks.manager import (
    CallbackManagerForLLMRun,
    AsyncCallbackManagerForLLMRun,
)
from langchain_core.messages import (
    BaseMessage,
    AIMessageChunk,
    HumanMessage,
    SystemMessage,
)
from langchain.embeddings.base import Embeddings
from sentence_transformers import SentenceTransformer

# Import the global logger
from lib.logger import setup_logger

# Initialize the logger for the models module
logger = setup_logger('gob-models')
# ... (rest of the file is the same)

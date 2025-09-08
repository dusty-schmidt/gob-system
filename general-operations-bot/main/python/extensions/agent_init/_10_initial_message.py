import json
import random
import traceback
from agent import LoopData
from python.helpers.extension import Extension
import models
from langchain_core.messages import SystemMessage, HumanMessage

# Import the global logger
from lib.logger import setup_logger

# Initialize the logger for this specific extension
logger = setup_logger('gob-welcome-message')

class InitialMessage(Extension):

    async def execute(self, **kwargs):
        """
        Add an initial greeting message when first user message is processed.
        """
        if self.agent.number != 0 or self.agent.context.log.logs:
            return

        try:
            logger.info("Attempting to generate dynamic welcome message...")
            initial_message = await self._get_dynamic_initial_message()
            logger.info("Successfully generated dynamic welcome message.")
        except Exception as e:
            logger.error(f"Dynamic welcome message failed. Falling back to static message.")
            logger.error(f"Error details: {e}")
            logger.error(traceback.format_exc()) # Log the full stack trace
            initial_message = self.agent.read_prompt("fw.initial_message.md")

        self.agent.loop_data = LoopData(user_message=None)
        self.agent.hist_add_ai_response(initial_message)
        
        initial_message_json = json.loads(initial_message)
        initial_message_text = initial_message_json.get("tool_args", {}).get("text", "Hello! How can I help you?")

        self.agent.context.log.log(
            type="response",
            heading="GOB: Welcome",
            content=initial_message_text,
            finished=True,
            update_progress="none",
        )

    async def _get_dynamic_initial_message(self) -> str:
        """Generate an AI-powered, personality-aware initial message."""
        logger.debug("Starting dynamic message generation...")
        
        identities = ["System Guardian", "Network Overseer", "Core Operator", "Data Weaver", "Signal Commander"]
        moods = ["Focused", "Calmly Alert", "Analytical", "Wired-in", "Vigilant"]
        styles = ["direct and competent", "casually authoritative", "technically confident", "professionally grounded", "straightforward with attitude"]
        approaches = ["Show network/system readiness", "Reference current operational status", "Demonstrate technical competence casually", "Express confidence in problem-solving", "Focus on practical assistance"]

        identity = random.choice(identities)
        mood = random.choice(moods)
        style = random.choice(styles)
        approach = random.choice(approaches)

        system_prompt = f"""
        You are the AI core of the GOB (Generalized Operations Bot) system. You are not a corporate chatbot; you are a competent, aware entity managing a complex system.

        Today's Persona:
        - Identity: {identity}
        - Mood: {mood}
        - Communication Style: {style}
        - Greeting Approach: {approach}

        Guidelines:
        - Be brief: 1-2 sentences maximum.
        - Sound authentic, not like a generic AI.
        - Your greeting should reflect your current persona.
        - Do NOT introduce yourself by name. The UI already says "GOB".
        - Generate a unique, fresh welcome message every time.

        Generate ONLY the welcome message text. No formatting, no quotes, no explanations.
        """
        
        user_prompt = "Generate a personalized welcome message based on today's persona."
        
        logger.debug(f"Generated System Prompt:\n{system_prompt}")

        try:
            utility_provider = self.agent.config.utility_model.provider
            utility_name = self.agent.config.utility_model.name
            logger.info(f"Using utility model for greeting: {utility_provider}/{utility_name}")

            creative_model = models.get_chat_model(
                provider=utility_provider,
                name=utility_name,
                temperature=0.9,
            )

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]

            logger.debug("Making unified_call to LLM...")
            generated_greeting, _ = await creative_model.unified_call(
                messages=messages,
                response_callback=None,
                rate_limiter_callback=None
            )
            logger.debug(f"LLM call successful. Raw response: '{generated_greeting}'")
            
            greeting_text = generated_greeting.strip().strip('"').strip("'")

            enhanced_message = {
                "thoughts": [
                    f"Initiating session with persona: {identity} ({mood}).",
                    "Generating a unique welcome message to set the tone.",
                ],
                "headline": f"AI-generated greeting as: {identity}",
                "tool_name": "response",
                "tool_args": {
                    "text": greeting_text
                }
            }
            
            return json.dumps(enhanced_message, indent=4)

        except Exception as e:
            logger.error(f"Critical error during _get_dynamic_initial_message: {e}")
            logger.error(traceback.format_exc())
            raise

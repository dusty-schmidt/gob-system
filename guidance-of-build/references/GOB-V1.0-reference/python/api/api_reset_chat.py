from agent import AgentContext
from python.helpers.api import ApiHandler, Request, Response
from python.helpers.print_style import PrintStyle
from python.helpers import persist_chat
import json


class ApiResetChat(ApiHandler):
    @classmethod
    def requires_auth(cls) -> bool:
        return False

    @classmethod
    def requires_csrf(cls) -> bool:
        return False

    @classmethod
    def requires_api_key(cls) -> bool:
        return True

    @classmethod
    def get_methods(cls) -> list[str]:
        return ["POST"]

    async def process(self, input: dict, request: Request) -> dict | Response:
        try:
            # Get context_id from input
            context_id = input.get("context_id")

            if context_id:
                # If context_id is provided, reset the existing chat
                context = AgentContext.get(context_id)
                if not context:
                    return Response(
                        '{"error": "Chat context not found"}',
                        status=404,
                        mimetype="application/json"
                    )
                context.reset()
                action_message = "Chat reset successfully"
            else:
                # If no context_id, create a new chat context
                context = AgentContext()
                context_id = context.id
                action_message = "New chat created successfully"

            # Save the context to persist the changes
            persist_chat.save_tmp_chat(context)

            # Log the action
            PrintStyle(
                background_color="#3498DB", font_color="white", bold=True, padding=True
            ).print(f"API Action: {action_message} for context: {context_id}")

            # Return success response
            return {
                "success": True,
                "message": action_message,
                "context_id": context_id
            }

        except Exception as e:
            PrintStyle.error(f"API reset chat error: {str(e)}")
            return Response(
                json.dumps({"error": f"Internal server error: {str(e)}"}),
                status=500,
                mimetype="application/json"
            )

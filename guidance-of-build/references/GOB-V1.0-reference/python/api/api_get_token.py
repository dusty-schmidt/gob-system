# /home/ds/sambashare/GOB/GOB-V1.0/python/api/api_get_token.py
from python.helpers.api import ApiHandler, Request, Response
from python.helpers.settings import create_auth_token

class ApiGetToken(ApiHandler):
    async def process(self, input: dict, request: Request) -> dict | Response:
        token = create_auth_token()
        return {"token": token}

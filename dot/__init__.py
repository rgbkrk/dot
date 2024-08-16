import asyncio
from typing import Callable, Dict
import json
import sys
import logging

from .command import create_command, PromptCommand


class ContextServer:
    commands: Dict[str, PromptCommand]

    def __init__(self):
        self.commands = {}

    def txt(self, func: Callable) -> Callable:
        command = create_command(func)

        self.commands[command.name] = command

        return func

    async def handle_request(self, request: Dict) -> Dict:
        try:
            method = request.get("method")
            params = request.get("params", {})
            logging.debug(f"Received request: {method}")
            logging.debug(f"Received params: {params}")

            if method == "initialize":
                return self.initialize(params)
            elif method == "prompts/list":
                return self.list_prompts()
            elif method == "prompts/get":
                return await self.get_prompt(params)
            else:
                logging.error(f"Unknown method: {method}")
                return {
                    "error": {"code": -32601, "message": f"Method not found: {method}"}
                }
        except Exception as e:
            logging.exception("Error handling request")
            return {"error": {"code": -32603, "message": str(e)}}

    def initialize(self, params: Dict) -> Dict:
        capabilities = {"prompts": {}}

        for name, command in self.commands.items():
            capabilities["prompts"][name] = command.dict()

        return {
            "result": {
                "protocolVersion": 1,
                "capabilities": capabilities,
                "serverInfo": {"name": "dot context server", "version": "0.1.0"},
            }
        }

    def list_prompts(self) -> Dict:
        prompts = [command.dict() for command in self.commands.values()]

        return {"result": {"prompts": prompts}}

    async def get_prompt(self, params: Dict) -> Dict:
        name = params.get("name")
        arguments = params.get("arguments", {})

        if name not in self.commands:
            return {"error": {"code": -32602, "message": f"Unknown prompt: {name}"}}

        command = self.commands[name]
        try:
            logging.debug(arguments)
            result = await command.func(**arguments)
            return {"result": {"prompt": result}}
        except Exception as e:
            return {"error": {"code": -32602, "message": str(e)}}

    async def run(self):
        logging.info("Context server started")
        while True:
            try:
                line = await asyncio.to_thread(sys.stdin.readline)
                if not line:
                    logging.info("Received EOF, shutting down")
                    break
                logging.debug(f"Received input: {line.strip()}")
                request = json.loads(line)
                response = await self.handle_request(request)
                response["jsonrpc"] = "2.0"
                response["id"] = request.get("id")
                json.dump(response, sys.stdout)
                sys.stdout.write("\n")
                sys.stdout.flush()
                logging.debug(f"Sent response: {json.dumps(response)}")
            except Exception as e:
                logging.exception("Error in main loop")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32603, "message": str(e)},
                }
                json.dump(error_response, sys.stdout)
                sys.stdout.write("\n")
                sys.stdout.flush()
        logging.info("Context server stopped")


context_server = ContextServer()
txt = context_server.txt

__all__ = ["txt", "context_server"]

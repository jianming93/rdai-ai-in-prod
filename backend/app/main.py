import os
from fastapi import FastAPI
import logging

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s", level=logging.INFO
)
from schemas.prompt_payload import PromptPayload, PromptResponse
from llm_client import LLMClient
from utils import format_prompt_payload

app = FastAPI()
llmclient = LLMClient(
    triton_server_url=os.environ["TRITON_SERVER_URL"],
    triton_server_port=os.environ["TRITON_SERVER_PORT"],
    triton_server_model_name=os.environ["TRITON_SERVER_MODEL_NAME"],
    triton_server_verbose=os.environ["TRITON_SERVER_VERBOSE"],
    streaming_mode=os.environ["TRITON_SERVER_STRAMING_MODE"],
    stream_timeout=os.environ["TRITON_SERVER_STREAM_TIMEOUT"],
)


@app.get("/")
async def welcome():
    return {"message": "Welcome to RDAI AI In Production Backend!"}


@app.post("/prompt")
async def prompt(payload: PromptPayload) -> PromptResponse:
    """Main endpoint for generation of results

    Args:
        payload (PromptPayload): Payload containing prompts and template.

    Returns:
        PromptResponse: The same payload with `results` as an additional key
            containing the results from the generation.
    """
    json_payload = payload.model_dump()
    prompt_string = format_prompt_payload(payload.model_dump())
    # output = await llmclient.run([prompt_string])
    logging.info("Input string: %s" % prompt_string)
    output = await llmclient.run([prompt_string], json_payload["config"])
    logging.info("Generated output %s" % output)
    # Remove template
    output = output.replace(json_payload["template"], "")
    logging.info("Formatted output %s" % output)
    json_payload["result"] = output
    return json_payload

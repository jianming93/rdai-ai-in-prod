from fastapi import FastAPI

from schemas.prompt_payload import PromptPayload, PromptResponse

app = FastAPI()

@app.get("/")
async def welcome():
    return {"message": "Welcome to RDAI AI In Production API!"}


@app.post("/prompt")
async def prompt(payload: PromptPayload) -> PromptResponse:
    """Main endpoint for generation of results

    Args:
        payload (PromptPayload): Payload containing prompts and template.

    Returns:
        PromptResponse: The same payload with `results` as an additional key
            containing the results from the generation.
    """
    print(payload)
    payload['results'] = "test"
    return payload
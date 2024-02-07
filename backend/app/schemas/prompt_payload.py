from pydantic import BaseModel, Extra, StrictStr


class MandatoryConfigMapping(BaseModel):
    temperature: StrictStr
    top_p: StrictStr
    max_tokens: StrictStr


class MandatoryPromptPayload(BaseModel):
    config: MandatoryConfigMapping
    system: StrictStr
    user: StrictStr
    template: StrictStr


class PromptPayload(MandatoryPromptPayload, extra=Extra.allow):
    "Payload for prompt"


class PromptResponse(PromptPayload):
    result: StrictStr

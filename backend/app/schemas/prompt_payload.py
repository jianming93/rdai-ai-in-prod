from pydantic import BaseModel, Extra, StrictStr


class MandatoryPromptPayload(BaseModel):
    system: StrictStr
    user: StrictStr
    template: StrictStr

class PromptPayload(MandatoryPromptPayload, extra=Extra.allow):
    "Payload for prompt"


class PromptResponse(PromptPayload):
    result: StrictStr

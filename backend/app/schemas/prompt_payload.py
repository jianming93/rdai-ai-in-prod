from pydantic import BaseModel, Extra, StrictStr


class MandatoryPromptPayload(BaseModel):
    system: StrictStr
    user: StrictStr
    template: StrictStr

class PromptPayload(MandatoryPromptPayload, extra=Extra.allow):


class PromptResponse(MandatoryPromptPayload, PromptPayload, extra=Extra.allow):
    result: StrictStr

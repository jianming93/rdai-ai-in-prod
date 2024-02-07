from typing import List
from pydantic import BaseModel, Extra, StrictStr, conlist


class EmbedderPayload(BaseModel):
    documents: conlist(item_type=StrictStr, min_length=1)


class EmbedderResponse(BaseModel):
    embeddings: List

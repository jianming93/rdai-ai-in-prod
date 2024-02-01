from typing import List
from pydantic import BaseModel, Extra, StrictStr, conlist


class EmbedderPayload(BaseModel):
    documents: conlist(item_type=StrictStr, min_items=[1])

class EmbedderResponse(BaseModel):
    embeddings: List

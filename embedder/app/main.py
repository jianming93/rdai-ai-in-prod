from fastapi import FastAPI
from transformers import AutoTokenizer, AutoModel
import torch

from schemas.prompt_payload import EmbedderPayload, EmbedderResponse

app = FastAPI()

tokenizer = AutoTokenizer.from_pretrained('BAAI/bge-large-zh-v1.5')
model = AutoModel.from_pretrained('BAAI/bge-large-zh-v1.5')
model.eval()

@app.get("/")
async def welcome():
    return {"message": "Welcome to RDAI AI In Production Embedder!"}


@app.post("/generate")
async def generate_embeddings(payload: EmbedderPayload) -> EmbedderResponse:
    """Main endpoint for generation of embeddings

    Args:
        payload (EmbedderPayload): Payload containing documents to generate embeddings.

    Returns:
        EmbedderResponse: The embedding results.
    """
    encoded_input = tokenizer(payload.documents, padding=True, truncation=True, return_tensors='pt')
    # Compute token embeddings
    with torch.no_grad():
        model_output = model(**encoded_input)
        # Perform pooling. In this case, cls pooling.
        sentence_embeddings = model_output[0][:, 0]
    # normalize embeddings
    sentence_embeddings = torch.nn.functional.normalize(sentence_embeddings, p=2, dim=1)
    return payload

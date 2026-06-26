import weaviate
from sentence_transformers import SentenceTransformer
import pandas as pd
from env import get_df

model = SentenceTransformer("all-MiniLM-L6-v2")
client = weaviate.connect_to_local()
df=get_df()

def get_client():
    client = weaviate.connect_to_local()
    return client

def get_embedding(text: str) -> list[float]:
    """
    Generate an embedding for the input text.
    """

    embedding = model.encode(
        text,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )

    return embedding.tolist()

def close_client(client):
    """
    Close the Weaviate connection.
    """
    client.close()

from agents import function_tool




   
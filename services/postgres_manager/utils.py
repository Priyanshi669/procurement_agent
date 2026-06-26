from sqlalchemy import create_engine
from openai import OpenAI
import os
from env import DB_URL

llm = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)
model="meta-llama/llama-3.3-70b-instruct"

engine = create_engine(DB_URL)

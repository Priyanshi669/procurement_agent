from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
from dotenv import load_dotenv
import os
import asyncio
from openai import AsyncOpenAI
from agents import ModelSettings
import pandas as pd
load_dotenv()

import pandas as pd

def get_df():
    return pd.read_csv("./Dataset/spend_analysis_dataset.csv")

client = AsyncOpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    max_retries=5,
)

MODEL_NAME ="openai/gpt-4.1-mini"

nvidia_model = OpenAIChatCompletionsModel(
    model=MODEL_NAME,
    openai_client=client
)

SETTINGS = ModelSettings(
    temperature=0.2,
    top_p=0.9,
    max_tokens=1024,
    parallel_tool_calls=False,
    
    # extra_body={
        
    #     "repetition_penalty": 1.05,
    #     "chat_template_kwargs": {
    #         "enable_thinking": False
    #     }
    # }
)
DB_URL= os.getenv("DB_URL")


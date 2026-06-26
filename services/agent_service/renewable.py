from typing import List

from agents import Agent
from pydantic import BaseModel

from env import nvidia_model, SETTINGS
from services.agent_service.schemas import renewable_instructions

from services.agent_service.tools import semantic_search, postgres_search, create_order
from services.weaviate_manager.retreival import OrderDetails


class RenewalResponse(BaseModel):

    reply: str

    found: bool

    orders: List[OrderDetails]

    confirmed: bool | None = None

    order_placed: bool = False

    error: bool = False   # distinguishes "tool/search failed" from "no results" or "user said no"


RenewableAgent = Agent(

    name="Renewable Agent",

    instructions=renewable_instructions,

    model=nvidia_model,

    model_settings=SETTINGS,

    output_type=RenewalResponse,
    tools=[
        semantic_search,
        postgres_search,
        create_order,
    ],
)
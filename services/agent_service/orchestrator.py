from agents import Agent, ModelSettings
from pydantic import BaseModel

from env import nvidia_model, SETTINGS
from services.agent_service.schemas import orchestrator_instructions




class OrchestratorOutput(BaseModel):
    reply: str
    product_name: str = ""
    title: str = ""
    type: str = "unknown"
    stop_flag: bool = False



Procure_hub= Agent(
        name="Procure Hub",
        instructions=orchestrator_instructions,
        model=nvidia_model,
        model_settings=SETTINGS,
        output_type=OrchestratorOutput,
    )
    
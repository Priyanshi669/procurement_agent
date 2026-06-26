import os
import asyncio
from pydantic import BaseModel, Field
from openai import AsyncOpenAI
from agents import Agent, Runner
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel

# 1. Define the desired structured output schema
class FinancialAnalysis(BaseModel):
    company_name: str = Field(description="The formal name of the company")
    ticker: str = Field(description="Stock ticker symbol")
    sentiment_score: float = Field(description="Market sentiment score from -1.0 to 1.0")
    key_takeaways: list[str] = Field(description="Bullet points outlining core growth drivers")

# 2. Configure the OpenAI client to point to Groq's API
groq_client = AsyncOpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# 3. Create the model wrapper with a supported Groq model
groq_model = OpenAIChatCompletionsModel(
    model="llama-3.3-70b-versatile",
    openai_client=groq_client
)

# 4. Initialize the agent with the defined output_type
analyst_agent = Agent(
    name="Market Analyst",
    instructions="Analyze the text and extract data strictly matching the schema.",
    model=groq_model,
    output_type=FinancialAnalysis  # Enforces structured output
)

async def main():
    user_input = "NVIDIA (NVDA) is seeing explosive demand for its Blackwell AI chips, driving record-breaking revenue."
    
    # Run the execution loop
    result = await Runner.run(analyst_agent, user_input)
    
    # The SDK automatically parses the JSON back into your Pydantic object
    structured_data: FinancialAnalysis = result.final_output
    
    print(f"Company: {structured_data.company_name} ({structured_data.ticker})")
    print(f"Sentiment: {structured_data.sentiment_score}")
    print(f"Takeaways: {structured_data.key_takeaways}")

if __name__ == "__main__":
    # Disable automated telemetry dashboard warnings if not using an OpenAI key
    os.environ["OPENAI_AGENTS_DISABLE_TRACING"] = "1"
    asyncio.run(main())
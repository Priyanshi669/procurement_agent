# import asyncio
# import uuid
# from services.postgres_manager.load import load_dataset
# from services.weaviate_manager.insertion import create_embeddings

# from services.agent_service.run import process_turn
# from services.weaviate_manager.utils import close_client


# async def main():

#     histories = {}
#     load_dataset()
#     create_embeddings()

#     active_agent = "orchestrator"

#     print("\nProcurement Agent Started")
#     print("Type 'exit' to quit\n")

#     user_message = "start"

#     while True:

#         reply, active_agent, histories = await process_turn(
#             user_message=user_message,
#             active_agent_name=active_agent,
#             histories=histories,
#         )

#         print("\nAssistant:")
#         print(reply)

#         user_message = input("\nYou: ")

#         if user_message.lower() == "exit":
#             break

#     close_client()


# if __name__ == "__main__":
#     asyncio.run(main())

# main.py
"""
FastAPI wrapper around process_turn(). No CLI loop -- the agent runs
once per HTTP request. Per-session state (active_agent + histories
dict) is kept in memory, keyed by session_id.

Run with: uvicorn main:app --reload
"""

# main.py
# main.py
"""
FastAPI wrapper around process_turn(). No CLI loop -- the agent runs
once per HTTP request. Per-session state (active_agent + histories
dict) is kept in memory, keyed by session_id.

IMPORTANT: Dataset/embedding seeding is NOT done here anymore. With
uvicorn --reload, this lifespan hook re-runs on every file save, which
was re-seeding Postgres and Weaviate repeatedly during development and
causing duplicate rows / inconsistent search results.

To seed the database, run this once, manually, BEFORE starting the API:
    python3 scripts/seed.py

Run the API with:
    uvicorn main:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from services.agent_service.run import process_turn
from services.weaviate_manager.utils import client, close_client
from services.postgres_manager.load import load_dataset
from services.weaviate_manager.insertion import create_embeddings
from services.weaviate_manager.utils import client, close_client


@asynccontextmanager
async def lifespan(app: FastAPI):
   
 

    print("Loading dataset into Postgres...")
    load_dataset()
 
    print("Creating Weaviate embeddings...")
    create_embeddings()
 
    print("Seeding complete.")
    close_client(client)
 
    # ---- STARTUP ----
    # No data seeding here on purpose -- see module docstring above.
    print("Startup complete.")

    yield

    # ---- SHUTDOWN ----
    print("Closing Weaviate client...")
    # close_client(client)  # adjust if close_client expects a different argument name/object


app = FastAPI(title="Procurement Agent API", lifespan=lifespan)

# In-memory store: session_id -> {"active_agent": str, "histories": dict}
# NOTE: resets if the process restarts. Swap for Redis/DB-backed storage
# if you need persistence across restarts or multiple workers.
SESSIONS: dict[str, dict] = {}


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    session_id: str
    active_agent: str
    reply: str


def _get_or_create_session(session_id: str) -> dict:
    if session_id not in SESSIONS:
        SESSIONS[session_id] = {
            "active_agent": "orchestrator",
            "histories": {},
        }
    return SESSIONS[session_id]


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="message cannot be empty")

    state = _get_or_create_session(req.session_id)

    try:
        reply, next_agent, histories = await process_turn(
            user_message=req.message,
            active_agent_name=state["active_agent"],
            histories=state["histories"],
        )
    except Exception as e:
        print(f"[/chat] process_turn failed for session {req.session_id}: {e!r}")
        raise HTTPException(status_code=500, detail="Something went wrong processing your message.")

    state["active_agent"] = next_agent
    state["histories"] = histories

    return ChatResponse(
        session_id=req.session_id,
        active_agent=next_agent,
        reply=reply,
    )


@app.post("/reset/{session_id}")
async def reset_session(session_id: str):
    """Start a fresh conversation for this session_id (e.g. after an order is placed)."""
    SESSIONS.pop(session_id, None)
    return {"status": "reset", "session_id": session_id}


@app.get("/health")
async def health():
    return {"status": "ok"}
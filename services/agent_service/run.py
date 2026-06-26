from agents import Runner

from services.agent_service.orchestrator import Procure_hub
from services.agent_service.renewable import RenewableAgent
from services.agent_service.non_renewable import NonRenewableAgent


AGENTS = {
    "orchestrator": Procure_hub,
    "renewable": RenewableAgent,
    "non_renewable": NonRenewableAgent,
}


async def process_turn(
    user_message: str,
    active_agent_name: str,
    histories: dict,   # {"orchestrator": [...], "renewable": [...], "non_renewable": [...]}
):
    print("\n" + "=" * 60)
    print(f"Current Agent : {active_agent_name}")
    print(f"User Message  : {user_message}")

    
    agent_history = histories.setdefault(active_agent_name, [])
    agent_history.append({"role": "user", "content": user_message})

    current_agent = AGENTS[active_agent_name]
    result = await Runner.run(current_agent, agent_history)
    output = result.final_output

    
    histories[active_agent_name] = result.to_input_list()

    print(f"\n----- {active_agent_name.upper()} Output -----")
    print(type(output))
    print(output)


    if active_agent_name == "orchestrator":

        if not output.stop_flag:
            print("Still collecting information")
            return output.reply, "orchestrator", histories

        print("\nCollection Complete")
        print(f"Product : {output.product_name}")
        print(f"Title   : {output.title}")
        print(f"Type    : {output.type}")

        next_agent = "renewable" if output.type.lower() == "renewal" else "non_renewable"
        print(f"\nRouting -> {next_agent}")

      
        histories[next_agent] = []

        return output.reply, next_agent, histories


    elif active_agent_name == "renewable":

        if getattr(output, "error", False):
            print("Tool/search failure -- staying on renewable, not routing.")
            return output.reply, "renewable", histories

        if getattr(output, "confirmed", None) is False:
            print("User rejected renewal. Routing to NonRenewableAgent")
            histories["non_renewable"] = []  # clean slate for non_renewable too
            return output.reply, "non_renewable", histories

        if getattr(output, "order_placed", False):
            print("Order placed.")
            histories["orchestrator"] = []  # reset for the next procurement request
            return output.reply, "orchestrator", histories

        return output.reply, "renewable", histories

  

    elif active_agent_name == "non_renewable":

        if getattr(output, "order_placed", False):
            print("Order placed.")
            histories["orchestrator"] = []
            return output.reply, "orchestrator", histories

        return output.reply, "non_renewable", histories
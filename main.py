from src.models.model import Model
from src.controllers.controller import Controller
from src.planners.planner import Planner
from src.agents.agent import Agent
from src.utils.utils import print_banner

if __name__ == "__main__":
    # Print a banner message
    print_banner("MCP LangGraph Framework Demo")

    # Initialize components
    model = Model(name="DemoModel")
    controller = Controller()
    planner = Planner()

    # Create an agent
    agent = Agent(model, controller, planner)

    # Example task
    task = "Write a greeting message."
    results = agent.act(task)

    # Print results
    for result in results:
        print(result) 
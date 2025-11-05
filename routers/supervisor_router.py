from langgraph.types import Command
from typing import Literal

from agents.utils import State

def router(state: State) -> Command[Literal["stock_agent", "search_agent"]]:
    next_step = state['next']
    return Command(goto=next_step)
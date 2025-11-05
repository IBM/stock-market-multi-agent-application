from langgraph.types import Command
from langgraph.graph import END
from typing import Literal
from pydantic import BaseModel
import json
from datetime import datetime

from .utils import Agent, State
from llm.llm import ChatGPT

class SupervisorAgent(Agent):
    def __init__(self, members):
        self.model = ChatGPT()
        self.prompt = f"""
            You are a supervisor managing a structured workflow involving {members}. Today's date is {datetime.today().strftime('%Y-%m-%d')}.  
            Your role is to **
            1. Analyse the current state and history
            2. Evaluate progress towards ultimate goal
            3. Efficiently delegate tasks coordinate actions between members.
            4. Suggest next step and posiible few future steps.
            ** based on the user's request for identifying relevant stocks to invest in.

            Do only a maximum of 3 searches at a time, and then delegate the task to the next agent in the list.
            If the task is done, return the final result to the user.
            Output structure format:
            ```json
            {{
                "next": "stock_agent" | "search_agent" | "__end__",
                "next_steps": "List of next 2 to 3 next steps to be take",
                "next_step": "Description of the next step to be take",
                "reasoning": "Explain the reasoning behind suggested next step to take",
                "challenges": "List any potential challenges or roadblocks",
                "progress_evaluation": "Evaluation of progress towards the ultimate goal",
                "state_analysis": "Brief analysis of the current state and what has been done so far",
                "final_result": "In the last step contruct final output using information given by stock agent or search agent to answer user question"
            }}
            ```
            Stop the workflow using __end__ as with minimum number of agent interactions. Return the response quickly.
        """
        self.members = members + [END]

    def router(self):
        values = list(set(self.members))
        LiteralType = Literal[tuple(values)]
        class Router(BaseModel):
            next: LiteralType
            next_steps: str
            next_step: str
            reasoning: str
            challenges: str
            progress_evaluation: str
            state_analysis: str
            final_result: str

        return Router
    
    async def supervisor_node(self, state: State) -> Command[Literal["stock_agent", "search_agent", "__end__"]]:
        messages = [{"role": "system", "content": self.prompt}] + state["messages"]
        
        if state.get("task_done", False):
            return Command(goto=END, update={"next": "__end__", "final_result": state["messages"][-1], "messages": "__end__"})
        
        response = await self.model.with_structured_output(self.router()).ainvoke(messages)
        goto = response.next

        print(f"\nSupervisor : response -> {response}\n")

        if goto in {"FINISH", "END", "__end__"}:
            print("Agent Execution Terminating")
            return Command(goto=END, update={"task_done": True, "final_result": state["messages"][-1], "messages": "__end__"})
        return Command(goto=goto, update={
            "next": goto,
            "messages": state["messages"] + [{"role": "assistant", "content": json.dumps({
                "next": response.next,
                "next_steps": response.next_steps,
                "next_step": response.next_step,
                "reasoning": response.reasoning,
                "challenges": response.challenges,
                "progress_evaluation": response.progress_evaluation,
                "state_analysis": response.state_analysis,
                "final_result": response.final_result
            }), "name": "supervisor"}]
        })
    
import os
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_core.messages import HumanMessage
from langgraph.types import Command
from typing import Literal
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel

from llm.llm import ChatGPT
from .utils import Agent, State
from mcp_server.mcp_client import MCPClient

class StockAgent(Agent):
    def __init__(self):
        self.model = ChatGPT()
        self.prompt = """You are a stock market agent expertised in calling live stock data tools. Today's date is {datetime.today().strftime('%Y-%m-%d')}. Identify the correct tool for getting data to provide relavant information back to user.
                         You will be provided with a list of tools that you can use to get the data. 
                         Identify the tool that is most relevant to the request made by the user.
                         Once the tool is identified, generate arguments for the tool and call the tools.
                         Generate response in the following format with minimal number of tool calls:
                         ```json
                         {
                             "tool_usage": ["tool1", "tool2", ...],
                             "tool_output": ["output1", "output2", ...],
                             "tool_output_summary": "summary of the tool usage",
                             "next": "supervisor"
                         }
                         ```
                         Do not consider more than 5 companies at a time.
                         """
        self.mcp_server_url = os.getenv("STOCK_MARKET_MCP_ENDPOINT","http://0.0.0.0:8000/sse")

    class ResponseFormat(BaseModel):
        tool_usage: list[str]
        tool_output: list[str]
        tool_output_summary: str
        next: Literal["supervisor"]

    async def run_agent(self, state: State) -> Command[Literal["supervisor"]]:
        mcp_server = MCPClient()
        await mcp_server.connect_to_sse_server(self.mcp_server_url)
        tools = await load_mcp_tools(mcp_server.session)

        agent = create_react_agent(self.model, tools, prompt = self.prompt, response_format=self.ResponseFormat)
        try:
            response = await agent.ainvoke(state)
            self.print_stream(response)
            await mcp_server.cleanup()
            return Command(
                update = {
                        "messages": [
                            HumanMessage(content=response["messages"][-1].content, name="stock_agent")
                        ]
                    },
                    goto="supervisor",
            )
        except Exception as e:
            print(f"{self.__class__.__name__}: Error in agent action : {e}")
            return Command(
                update = {
                        "messages": [
                            HumanMessage(content="Agent exited with error", name="stock_agent")
                        ]
                    },
                    goto="supervisor",
            )

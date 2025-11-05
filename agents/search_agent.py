from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel
from langgraph.types import Command
from typing import Literal

from llm.llm import ChatGPT
from .utils import Agent, State

class SearchAgent(Agent):
    def __init__(self):
        self.model = ChatGPT()
        self.prompt = """You are a helpful assistant capable of searching the internet to generate content and satisfy user requests. Today's date is {datetime.today().strftime('%Y-%m-%d')}.  
                         Generate output for incoming request from supervior agent using available tools `internet search tool` and return response back to supervisor in a summarised list item format
                         Generate a response in the following format with minnimal number of tool calls:
                         ```json
                         {
                             "search_results": ["result1", "result2", ...],
                             "search_query": "query used for search",
                             "search_summary": "summary of the search results",
                             "next": "supervisor"
                         }
                         ```
                         """

    class ResponseFormat(BaseModel):
        search_results: list[str]
        search_query: str
        search_summary: str
        next: Literal["supervisor"]

    async def run_agent(self, state: State) -> Command[Literal["supervisor"]]:
        tools = load_tools(['google-serper'])
        
        agent = create_react_agent(self.model, tools, prompt = self.prompt, response_format=self.ResponseFormat)
        try:
            response = await agent.ainvoke(state)
            self.print_stream(response)
            return Command(
                update = {
                        "messages": [
                            HumanMessage(content=response["messages"][-1].content, name="search_agent")
                        ]
                    },
                    goto="supervisor",
            )
        except Exception as e:
            print(f"{self.__class__.__name__}: Error in agent action : {e}")
            return Command(
                update = {
                        "messages": [
                            HumanMessage(content="Agent exited with error", name="search_agent")
                        ]
                    },
                    goto="supervisor",
            )


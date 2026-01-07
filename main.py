import os
import sys
import json
from prompts.prompts import Prompt

input_query = json.loads(sys.argv[1])
print(input_query)

input_query = Prompt(**input_query)
print(input_query)
model = os.getenv("MODEL")
traceloop_log_file_path = f"trace_dataset/{input_query.id}_{model.replace("/", "_")}.log"

from opentelemetry.sdk.trace.export import ConsoleSpanExporter
exporter = ConsoleSpanExporter(out=open(traceloop_log_file_path, "w"))

from traceloop.sdk import Traceloop
from traceloop.sdk.decorators import workflow
Traceloop.init(app_name="StockMarketAgent", exporter=exporter)

import asyncio
from langgraph.graph import StateGraph, START, END

from agents.stock_agent import StockAgent
from agents.search_agent import SearchAgent
from agents.supervisor import SupervisorAgent
from agents.utils import State
from routers.supervisor_router import router
from prompts.prompts import PromptDataset

@workflow(name="stock_market_agent_workflow")
async def run_agent(input_prompt):
    print(input_prompt)
    branches = ['stock_agent', 'search_agent', END]

    supervisor_agent = SupervisorAgent(branches)
    stock_agent = StockAgent()
    search_agent = SearchAgent()

    graph = StateGraph(State)
    graph.add_node("supervisor", supervisor_agent.supervisor_node)
    graph.add_node("stock_agent", stock_agent.run_agent)
    graph.add_node("search_agent", search_agent.run_agent)
    
    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges("supervisor", router)
    graph.add_edge("supervisor", END)

    compiled_graph = graph.compile()

    graph_image = compiled_graph.get_graph().draw_mermaid_png()
    with open("docs/graph.png", "wb") as f:
        f.write(graph_image)
    
    response = await compiled_graph.ainvoke({"messages": [("user", input_prompt.prompt)]})
    print("Final response:", response)

asyncio.run(run_agent(input_query))

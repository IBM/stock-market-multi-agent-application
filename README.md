# StockMarketAgent

## Components
1. Supervisor agent
2. Live stock analysis agent
3. Search agent
4. Stocks MCP Server

## Env vars Setup
`cp .env.example .env`

Configure `.env` with correct model name, base url and api key for LLM and Serper.

## Running the code
1. MCP server
`python mcp_server/stockflow_mcp.py`

2. Agent
`python main.py <input args>`

Eg: `python main.py '{"id": "1d37b5dd23694bb286617626530de24b","prompt": "Compare the performance of Amazon and Apple over the last month."}'`

This should create a file which starts with name `1d37b5dd23694bb286617626530de24b*.log` in `trace_dataset` folder.

3. RUN Experiment Suite
`python run_exp.py`

Traces are stored in `trace_dataset` folder.
This will start MCP server and executes prompts one after another from prompt_dataset
Live stock analysis agent interacts with MCP server running on `0.0.0.0:8000` port.

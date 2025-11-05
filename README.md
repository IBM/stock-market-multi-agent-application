# StockMarketAgent

## Components
1. Supervisor agent
2. Live stock analysis agent
3. Search agent
4. Stocks MCP Server

## Env vars Setup
export RITS_API_KEY=*****
export SERPER_API_KEY=*****
export OTEL_EXPORTER_OTLP_INSECURE=true
export TRACELOOP_METRICS_ENABLED=false

## Running the code
1. MCP server
`python mcp_server/stockflow_mcp.py`

2. Agent
`python main.py <input args>`

3. RUN Experiment
`python run_exp.py`

Traces are stored in 
This will start MCP server and executes prompts one after another from prompt_dataset
Live stock analysis agent interacts with MCP server running on `0.0.0.0:8000` port.

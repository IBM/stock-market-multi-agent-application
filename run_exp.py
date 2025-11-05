from prompts.prompts import PromptDataset
import subprocess
import json
import time

def run_iteratively(inputs):
    l = len(inputs)
    index = 1
    for input_prompt in inputs:
        print(f"{index} out of total:{l}")
        mcp = subprocess.Popen(["python", "mcp_server/stockflow_mcp.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"MCP : {mcp}")

        p = subprocess.Popen(["python", "main.py", json.dumps(input_prompt.model_dump(mode='json'))], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, errors = p.communicate()
        print(f"Final response: {output}, \nerrors:{errors}\nreturncode: {p.returncode}")
        mcp.kill()
        time.sleep(60)
        index += 1

inputs = PromptDataset().get_prompts()
run_iteratively(inputs)

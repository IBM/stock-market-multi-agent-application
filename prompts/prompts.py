import os
import json
import uuid
from pydantic import BaseModel
from random import shuffle
from itertools import combinations

class PromptTemplate(BaseModel):
    template: str

class Prompt(BaseModel):
    id: str
    prompt: str

prompt_json = "prompts.json"
prompt_dataset_folder = "prompts/prompt_dataset"
trace_dataset_folder = "prompts/trace_dataset"

def load_prompt_templates(filename, category) -> list[PromptTemplate]:
    with open(filename, "r") as file:
        templates = json.load(file)[category]
    return [PromptTemplate(**template) for template in templates]

def get_all_combination(indexes):
    return list(combinations(indexes, 2))

def generate_complete_prompt(indexes, prompt_templates):
    updated_prompts = []
    if f"{{index1}}" and f"{{index2}}" in prompt_templates[0].template:
        comb = get_all_combination(indexes)
        for c in comb:
            for prompt_template in prompt_templates:
                id = f"{uuid.uuid4().hex}"
                template = prompt_template.template.replace(f"{{index1}}", c[0])
                template = template.replace(f"{{index2}}", c[1])
                updated_prompts.append(Prompt(id=id, prompt=template))
        return [p.model_dump(mode='json') for p in updated_prompts]

    if f"{{index}}" in prompt_templates[0].template:
        for index in indexes:
            for prompt_template in prompt_templates:
                id = f"{uuid.uuid4().hex}"
                template = prompt_template.template.replace(f"{{index}}", index)
                updated_prompts.append(Prompt(id=id, prompt=template))
        return [p.model_dump(mode='json') for p in updated_prompts]
    
    else:
        for prompt_template in prompt_templates:
            id = f"{uuid.uuid4().hex}"
            updated_prompts.append(Prompt(id=id, prompt=prompt_template.template))
        return [p.model_dump(mode='json') for p in updated_prompts]


# Create dataset for the 'get_share_price_prompts' category
def create_prompt_dataset():
    categories = ['get_share_price_prompts', 'get_stock_news_prompts', 'get_stock_analysis_prompts', 'get_stock_trends_prompts', 'get_stock_forecast_prompts', 'get_share_performce_comparison_prompts']
    indexes = ['Amazon', 'Apple', 'Google', 'Microsoft', 'Tesla']
    for category in categories:
        prompt_templates = load_prompt_templates(prompt_json, category)
        dataset = generate_complete_prompt(indexes, prompt_templates)
        file = f"{prompt_dataset_folder}/{category}.json"

        with open(file, "w") as f:
            json.dump(dataset, f, indent=4)
        print(f"Dataset saved to {file}")

class PromptDataset:
    def __init__(self):
        self.categories = ['get_share_price_prompts', 'get_stock_news_prompts', 'get_stock_analysis_prompts', 'get_stock_trends_prompts', 'get_stock_forecast_prompts', 'get_share_performce_comparison_prompts']
        self.prompts = self.load_prompts()

    def load_prompts(self):
        result = []
        files = os.listdir(trace_dataset_folder)
        completed_prompts = [i.split('.')[0] for i in files if i.endswith(".log")]
        completed_prompts = [i.split('_')[0] for i in completed_prompts]
        print(f"Completed {len(completed_prompts)} prompts")

        for category in self.categories:
            file = f"{prompt_dataset_folder}/{category}.json"
            with open(file, "r") as f:
                prompts = json.load(f)
            result = result + [Prompt(**prompt) for prompt in prompts if prompt['id'] not in completed_prompts]
        return result

    def get_prompts(self):
        shuffle(self.prompts)
        return self.prompts

# create_prompt_dataset()
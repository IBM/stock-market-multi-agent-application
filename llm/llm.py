import os
from langchain_openai import ChatOpenAI

class ChatLLM(ChatOpenAI):
    def __init__(self, **kwargs):
        model_name = kwargs.get("model", kwargs.get("model_name"))
        if model_name is None:
            raise ValueError("model or model_name is required")
        
        kwargs.setdefault("model_name", model_name)
        kwargs.setdefault("api_key", "/")
        kwargs.setdefault("default_headers", {"RITS_API_KEY": os.getenv("RITS_API_KEY")})
        kwargs.setdefault(
            "base_url",
            f"{os.getenv("RITS_BASE_URL")}"
            f"{model_name.split('/')[1].strip().lower().replace('.', '-')}/v1"
        )
        super().__init__(**kwargs)

class ChatGPT(ChatOpenAI):
    def __init__(self, **kwargs):
        kwargs.setdefault("openai_api_base", os.getenv("OPENAI_BASE_URL"))
        kwargs.setdefault("model", os.getenv("MODEL"))
        super().__init__(**kwargs)
        
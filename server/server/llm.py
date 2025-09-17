import os

from langchain_openai import ChatOpenAI

from server.settings import settings

os.environ["OPENAI_API_KEY"] = settings.openai_api_key

llm = ChatOpenAI(
    model="gpt-5-nano",
    verbosity="low",
    reasoning_effort="low",
    max_tokens=512,
)

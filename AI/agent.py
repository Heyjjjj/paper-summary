# -*- coding: utf-8 -*-
from langchain.agents import create_agent
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import tool

@tool(description="weather")
def get_weather():
    return "sun day"

agent = create_agent(
    model=ChatTongyi(
        model="tongyi-xiaomi-analysis-flash",
        api_key="sk-95efe5f35b934a9e9114d2daad4d7d8a",
        ),
    tools=[get_weather],
    system_prompt='You are a chat assistant, answering user questions',
)

res = agent.invoke(
    {"messages":[
        {"role":"user","content":"What's the weather like in Shenzhen tomorrow"}
    ]}
)
print(res)
parser = StrOutputParser()
for msg in res["messages"]:
    print(f"{type(msg).__name__}:{parser.invoke(msg)}")
from langchain.agents import create_agent
from langchain.agents.middleware import *
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import tool

@before_agent

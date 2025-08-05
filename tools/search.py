import requests
import sys
import os
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

API_KEY = os.getenv("SEARCH_API_KEY")

class BaiduSearchInput(BaseModel):
    """百度搜索工具的输入"""
    query: str = Field(..., description="搜索关键词")

class BaiduSearchTool(BaseTool):
    """使用百度搜索API进行联网搜索的工具"""
    
    name: str = "baidu_search_tool"
    description: str = "使用百度搜索API进行联网搜索，返回搜索结果的字符串。"
    args_schema: Type[BaseModel] = BaiduSearchInput

    def _run(self, query: str) -> str:
        """
        使用百度搜索API进行联网搜索，返回搜索结果的字符串。

        参数:
        - query: 搜索关键词

        返回:
        - 搜索结果的字符串形式
        """
        url = 'https://qianfan.baidubce.com/v2/ai_search/chat/completions'
        headers = {
            'Authorization': f'Bearer {API_KEY}',  # 从环境变量获取API密钥
            'Content-Type': 'application/json'
        }
        messages = [
            {
                "content": query,
                "role": "user"
            }
        ]
        data = {
            "messages": messages,
            "search_source": "baidu_search_v2",
            "model": "deepseek-r1"
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            # 返回给大模型的格式化的搜索结果文本
            return str(response.json())
        else:
            raise Exception(f"API请求失败, 状态码: {response.status_code}, 错误信息: {response.text}")
# 打印工具名称, 描述, 参数等 名称正确、文档正确且类型提示正确的工具更易于模型使用
# print(baidu_search_tool.name)
# print("----------------------------------------------------------------------------------------------------------------")
# print(baidu_search_tool.description)
# print("----------------------------------------------------------------------------------------------------------------")
# print(baidu_search_tool.args)
# print("----------------------------------------------------------------------------------------------------------------")

tools = [BaiduSearchTool()]

# from ..llms import get_zhipu_ai_llm
from llms import get_zhipu_ai_llm
llm = get_zhipu_ai_llm()

# 创建代理并调用工具
# agent_scratchpad 是一个占位符，用于存储Agent执行过程中的中间步骤
# intermediate_steps 包含实际的工具调用和结果
print("\n使用AgentExecutor执行工具调用:")
prompt = ChatPromptTemplate.from_template("今天{city}天气怎么样 {agent_scratchpad}")
agent = create_tool_calling_agent(llm, tools, prompt)
# 设置return_intermediate_steps=True以返回中间步骤
# agent_executor = AgentExecutor(agent=agent, tools=tools, return_intermediate_steps=True)
agent_executor = AgentExecutor(agent=agent, tools=tools)

# 执行Agent并获取结果
result = agent_executor.invoke({"city":"河南省信阳市光山县", "agent_scratchpad":"intermediate_steps"})
print("Agent执行结果:")
print(result)
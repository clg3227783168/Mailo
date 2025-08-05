from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llms import get_zhipu_ai_llm
from tools.mail import UniversalEmailTool, UniversalEmailToolReading
# 初始化工具
tools = [UniversalEmailTool(), UniversalEmailToolReading()]

# 初始化语言模型
llm = get_zhipu_ai_llm()

# 创建适合邮件助手的prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业的邮件助手，可以帮助用户发送和阅读邮件。请根据用户的请求执行相应的操作。"),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# 创建代理
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 发送邮件
result = agent_executor.invoke({
    "input": "向2586544679@qq.com发送一封主题为'测试'，内容为'你好,mengjin 吃面吗'的邮件"
})

# 读取邮件
# result = agent_executor.invoke({
#     "input": "阅读并总结我最近的3封邮件"
# })
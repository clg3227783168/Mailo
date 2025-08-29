import os
import sys
from typing import Type, Optional

from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

# 将父目录添加到系统路径中，以便可以导入llm
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llms import get_zhipu_ai_llm

class FormatMarkdownInput(BaseModel):
    """Markdown格式化工具的输入模型"""
    input_path: str = Field(..., description="需要格式化的Markdown文件的路径。")
    output_path: Optional[str] = Field(None, description="可选：保存格式化后文件的路径。如果未提供，将覆盖原文件。")

class MarkdownFormattingTool(BaseTool):
    """一个使用大语言模型格式化Markdown文件的工具"""
    name: str = "markdown_formatting_tool"
    description: str = "通过修正结构和移除多余字符来格式化一个Markdown文件，然后将其保存。不会改变文本的原始意义。"
    args_schema: Type[BaseModel] = FormatMarkdownInput

    def _run(self, input_path: str, output_path: Optional[str] = None) -> str:
        """执行工具"""
        try:
            llm = get_zhipu_ai_llm()

            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()

            prompt = ChatPromptTemplate.from_messages([
                ("system", "你是一个文本格式化专家。你的任务是将以下文本转换为一个干净、结构良好的Markdown格式。请修正所有格式错误，并移除任何多余的字符或标记。最重要的是，绝不能改变文本的原始意义。你的输出应该只有格式化后的Markdown文本。 "),
                ("user", "{text_input}")
            ])
            
            chain = prompt | llm
            
            response = chain.invoke({"text_input": content})
            
            formatted_content = response.content if hasattr(response, 'content') else str(response)

            if output_path is None:
                output_path = input_path
            
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(formatted_content)
            
            return f"成功格式化 {input_path} 并保存到 {output_path}"

        except FileNotFoundError:
            return f"错误: 在路径 {input_path} 未找到输入文件"
        except Exception as e:
            return f"发生错误: {e}"

# --- 使用示例 ---
if __name__ == '__main__':
    from langchain.agents import AgentExecutor, create_tool_calling_agent

    # 为测试创建一个临时文件
    if not os.path.exists("test_docs"):
        os.makedirs("test_docs")
    test_file = "test_docs/test_format.md"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("  #这是一个   格式不佳的标题\n\n  这里是带有多余   空格的文本。\n\n- 项目 1\n-  项目 2\n\n一些冗余字符&&&")

    tools = [MarkdownFormattingTool()]
    llm = get_zhipu_ai_llm()

    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个乐于助人的助手。"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    result = agent_executor.invoke({
        "input": f"请格式化位于 {test_file} 的Markdown文件，并将其保存到 test_docs/formatted_test.md"
    })
    print(result)

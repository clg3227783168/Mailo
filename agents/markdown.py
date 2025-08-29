from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llms import get_zhipu_ai_llm
# 初始化大语言模型
llm = get_zhipu_ai_llm()

def format_markdown_from_file(file_path: str) -> str:
    """
    利用大语言模型将文本文件内容转换为格式正确的Markdown。

    参数:
        file_path (str): 输入的文本文件路径。

    返回:
        str: 经过LLM格式化后的Markdown文本。
    """
    # 注意: 此处假设运行环境能正确读取文件。
    # 如果遇到编码问题，您可能需要用特定的编码格式（如'gbk'）来处理文件读取。
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个文本格式化专家。你的任务是将以下文本转换为一个干净、结构良好的Markdown格式。请修正所有格式错误，并移除任何多余的字符或标记。最重要的是，绝不能改变文本的原始意义。你的输出应该只有格式化后的Markdown文本。"),
        ("user", "{text_input}")
    ])
    
    chain = prompt | llm
    
    response = chain.invoke({"text_input": content})
    
    # LLM的响应预计会有一个'content'属性。
    # 这可能需要根据您使用的具体LLM的返回结构进行调整。
    return response.content if hasattr(response, 'content') else str(response)

def format_and_save_markdown(input_path: str, output_path: str = None):
    """
    格式化Markdown文件并将其保存。

    参数:
        input_path (str): 输入文件的路径。
        output_path (str, optional): 输出文件的路径。如果为None，将覆盖原始文件。默认为None。
    """
    if output_path is None:
        output_path = input_path

    formatted_content = format_markdown_from_file(input_path)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(formatted_content)
    print(f"文件已成功格式化并保存到: {output_path}")

if __name__ == '__main__':
    import random

    processed_data_dir = "processed_data"
    format_data_dir = "format_data"

    # 确保输出目录存在
    if not os.path.exists(format_data_dir):
        os.makedirs(format_data_dir)

    try:
        # 获取所有文件名
        all_files = [f for f in os.listdir(processed_data_dir) if os.path.isfile(os.path.join(processed_data_dir, f))]
        # 随机选择一个文件
        selected_file = random.choice(all_files)
        input_path = os.path.join(processed_data_dir, selected_file)
        output_path = os.path.join(format_data_dir, selected_file)
        
        print(f"随机选择的文件: {input_path}")
        
        # 调用函数处理并保存文件
        format_and_save_markdown(input_path, output_path)

    except FileNotFoundError:
        print(f"错误: 找不到目录 '{processed_data_dir}'。请确保该目录存在。")
    except Exception as e:
        print(f"发生错误: {e}")


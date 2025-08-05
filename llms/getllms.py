from langchain_community.chat_models import ChatZhipuAI
import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# 智谱AI API密钥
ZHIPUAI_API_KEY = os.getenv("ZHIPUAI_API_KEY")

def get_zhipu_ai_llm():
    """
    创建并返回一个配置好的智谱AI大语言模型实例
    
    Returns:
        ChatZhipuAI: 配置好的智谱AI大语言模型实例
    """
    return ChatZhipuAI(
        temperature=0.5,
        model="glm-4.5",
        api_key=ZHIPUAI_API_KEY,
        openai_api_base="https://open.bigmodel.cn/api/paas/v4/"
    )
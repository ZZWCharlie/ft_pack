from langchain_openai import ChatOpenAI
import os

def get_response():
    llm = ChatOpenAI(
        api_key="sk-47351cfbc953455b8b90b4ded9bba351",  # 如果您没有配置环境变量，请用阿里云百炼API Key将本行替换为：api_key="sk-xxx"
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 填写DashScope base_url
        model="qwen-plus"    # 此处以qwen-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        )
    messages = [
        {"role":"system","content":"You are a helpful assistant."}, 
        {"role":"user","content":"你是谁？"}
    ]
    response = llm.invoke(messages)
    print(response.json())

if __name__ == "__main__":
    get_response()
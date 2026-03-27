import requests
import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 从环境变量读取 API Key
API_KEY = os.getenv("DEEPSEEK_API_KEY")

url = "https://api.deepseek.com/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "model": "deepseek-chat",
    "messages": [
        {"role": "user", "content": "你好，请简单介绍一下你自己"}
    ]
}

print("正在调用 DeepSeek API...")
response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    result = response.json()
    reply = result["choices"][0]["message"]["content"]
    print("\n回复：", reply)
else:
    print("调用失败，状态码：", response.status_code)
    print("错误信息：", response.text)
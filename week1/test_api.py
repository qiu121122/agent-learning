import requests

API_KEY = "sk-3843242ce0ae436e88185306e1fe1496"

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
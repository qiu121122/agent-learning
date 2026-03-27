import chromadb
import requests
import os
from dotenv import load_dotenv

load_dotenv()

client = chromadb.PersistentClient(path="./chroma_data")
collection = client.get_collection("test_collection")

def search(query, n_results=2):
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    return results['documents'][0]

def ask_deepseek(question, context):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    url = "https://api.deepseek.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""请基于以下资料回答问题。
资料：{context}
问题：{question}
回答："""
    
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}]
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"]

if __name__ == "__main__":
    question = input("请输入你的问题：")
    docs = search(question)
    context = "\n".join(docs)
    answer = ask_deepseek(question, context)
    print(f"\n问题：{question}")
    print(f"检索到的资料：{context}")
    print(f"答案：{answer}")
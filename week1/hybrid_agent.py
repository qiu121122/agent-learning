import chromadb
import sqlite3
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# 初始化 Chroma 客户端（用于 RAG）
client = chromadb.PersistentClient(path="./chroma_data")
collection = client.get_collection("test_collection")

def search_rag(query, n_results=2):
    """RAG 检索"""
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    return results['documents'][0]

def get_sql_schema():
    """获取数据库结构"""
    conn = sqlite3.connect("sales.db")
    cursor = conn.cursor()
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")
    schema = cursor.fetchall()
    conn.close()
    return "\n".join([s[0] for s in schema if s[0]])

def execute_sql(sql):
    """执行 SQL"""
    conn = sqlite3.connect("sales.db")
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        conn.close()
        return results
    except Exception as e:
        conn.close()
        return str(e)

def call_deepseek(prompt):
    """通用 API 调用"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    url = "https://api.deepseek.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}]
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"]

def classify_intent(question):
    """判断问题是知识型还是数据型"""
    prompt = f"""请判断以下问题属于哪一类，只回答"知识"或"数据"。

知识类：询问概念、定义、解释、原理等（例如：什么是AI？、RAG是什么？）
数据类：询问统计、数量、金额、排行等（例如：卖了多少？、哪个最多？）

问题：{question}
分类："""
    
    result = call_deepseek(prompt).strip()
    if "数据" in result:
        return "data"
    else:
        return "knowledge"

def handle_data_question(question):
    """处理数据类问题"""
    schema = get_sql_schema()
    
    # 生成 SQL
    prompt = f"""数据库结构：
{schema}

字段说明：
- product: 产品名称（笔记本、鼠标、键盘）
- amount: 销售数量
- date: 销售日期（格式 YYYY-MM-DD）

请根据以下问题生成 SQL 查询语句，只返回 SQL 语句本身，不要加任何解释或代码块标记。
问题：{question}
SQL："""
    
    sql = call_deepseek(prompt).strip()
    
    # 清理 Markdown 标记
    if sql.startswith("```sql"):
        sql = sql[6:]
    if sql.startswith("```"):
        sql = sql[3:]
    if sql.endswith("```"):
        sql = sql[:-3]
    sql = sql.strip()
    
    print(f"  [SQL] {sql}")
    
    # 执行 SQL
    result = execute_sql(sql)
    
    # 解释结果
    explain_prompt = f"""用户问题：{question}
查询结果：{result}
请用自然语言回答用户。"""
    
    answer = call_deepseek(explain_prompt)
    return answer

def handle_knowledge_question(question):
    """处理知识类问题"""
    # 检索相关文档
    docs = search_rag(question)
    context = "\n".join(docs)
    
    print(f"  [RAG] 检索到 {len(docs)} 条资料")
    
    # 生成答案
    prompt = f"""请基于以下资料回答问题。
资料：{context}
问题：{question}
回答："""
    
    answer = call_deepseek(prompt)
    return answer

if __name__ == "__main__":
    print("=" * 50)
    print("混合智能体 (RAG + SQL)")
    print("=" * 50)
    
    while True:
        question = input("\n请输入你的问题（输入 q 退出）：")
        if question.lower() == 'q':
            break
        
        print(f"\n正在分析...")
        
        # 1. 判断意图
        intent = classify_intent(question)
        print(f"  [意图] {intent}")
        
        # 2. 根据意图处理
        if intent == "data":
            answer = handle_data_question(question)
        else:
            answer = handle_knowledge_question(question)
        
        # 3. 输出答案
        print(f"\n答案：{answer}")
        print("-" * 50)
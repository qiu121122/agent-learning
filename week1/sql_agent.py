import sqlite3
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_sql_schema():
    """获取数据库结构"""
    conn = sqlite3.connect("sales.db")
    cursor = conn.cursor()
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")
    schema = cursor.fetchall()
    conn.close()
    return "\n".join([s[0] for s in schema if s[0]])

def ask_deepseek(prompt):
    """调用 DeepSeek API"""
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

def execute_sql(sql):
    """执行 SQL 并返回结果"""
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

if __name__ == "__main__":
    schema = get_sql_schema()
    question = input("请输入你的数据问题（例如：笔记本总共卖了多少？）：")
    
    # 让模型生成 SQL
    prompt = f"""数据库结构：
{schema}

字段说明：
- product: 产品名称（笔记本、鼠标、键盘）
- amount: 销售数量
- date: 销售日期

请根据以下问题生成 SQL 查询语句，只返回 SQL 语句本身，不要加任何解释或代码块标记。
问题：{question}
SQL："""
    
    sql = ask_deepseek(prompt).strip()
    
    # 清理 Markdown 代码块标记
    if sql.startswith("```sql"):
        sql = sql[6:]
    if sql.startswith("```"):
        sql = sql[3:]
    if sql.endswith("```"):
        sql = sql[:-3]
    sql = sql.strip()
    
    print(f"\n生成的 SQL：{sql}")
    
    # 执行 SQL
    result = execute_sql(sql)
    print(f"查询结果：{result}")
    
    # 让模型解释结果
    explain_prompt = f"""用户问题：{question}
查询结果：{result}
请用自然语言回答用户。"""
    
    answer = ask_deepseek(explain_prompt)
    print(f"回答：{answer}")
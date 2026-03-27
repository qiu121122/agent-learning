import chromadb
import sqlite3
import requests
import os
import math
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from typing import TypedDict

load_dotenv()

# ==================== 定义状态 ====================
class AgentState(TypedDict):
    question: str        # 用户问题
    intent: str          # 意图：knowledge / data / calculator
    answer: str          # 最终答案

# ==================== 初始化 Chroma ====================
client = chromadb.PersistentClient(path="./chroma_data")
collection = client.get_collection("test_collection")

# ==================== 通用 API 调用 ====================
def call_deepseek(prompt):
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

# ==================== RAG 检索 ====================
def search_rag(query):
    """从 Chroma 检索最相似的文档"""
    results = collection.query(
        query_texts=[query],
        n_results=1
    )
    if results['documents'][0]:
        return results['documents'][0][0]
    return ""

# ==================== 节点1：判断意图 ====================
def classify_node(state: AgentState):
    """判断问题是知识类、数据类还是计算类"""
    question = state["question"]
    
    prompt = f"""判断以下问题属于哪一类，只回答"knowledge"、"data"或"calculator"。

知识类（knowledge）：询问概念、定义、解释、原理（例如：什么是AI？、RAG是什么？）
数据类（data）：询问统计、数量、金额、排行（例如：卖了多少？、哪个最多？）
计算类（calculator）：要求做数学计算（例如：25*4等于多少？、100除以5是多少？）

问题：{question}
类型："""
    
    result = call_deepseek(prompt).strip().lower()
    
    if "knowledge" in result:
        intent = "knowledge"
    elif "data" in result:
        intent = "data"
    else:
        intent = "calculator"
    
    print(f"  [意图判断] {intent}")
    return {"intent": intent}

# ==================== 节点2：知识类处理（RAG） ====================
def knowledge_node(state: AgentState):
    """用 RAG 回答问题"""
    question = state["question"]
    
    context = search_rag(question)
    print(f"  [RAG] 检索到资料：{context[:50]}..." if context else "  [RAG] 未检索到资料")
    
    if context:
        prompt = f"""请基于以下资料回答问题。

资料：{context}

问题：{question}

回答："""
    else:
        prompt = f"""请回答问题（资料库中没有相关信息，请用自己的知识回答）。

问题：{question}

回答："""
    
    answer = call_deepseek(prompt)
    return {"answer": answer}

# ==================== 节点3：数据类处理（SQL） ====================
def sql_node(state: AgentState):
    """用 SQL 查询数据"""
    question = state["question"]
    
    # 获取数据库结构
    conn = sqlite3.connect("sales.db")
    cursor = conn.cursor()
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")
    schema = cursor.fetchall()
    conn.close()
    schema_str = "\n".join([s[0] for s in schema if s[0]])
    
    # 让模型生成 SQL
    prompt = f"""数据库结构：
{schema_str}

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
    conn = sqlite3.connect("sales.db")
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
        conn.close()
        result_str = str(result)
        print(f"  [结果] {result_str}")
    except Exception as e:
        conn.close()
        result_str = str(e)
        print(f"  [错误] {result_str}")
    
    # 让模型解释结果
    explain_prompt = f"""用户问题：{question}
查询结果：{result_str}
请用自然语言回答用户。"""
    
    answer = call_deepseek(explain_prompt)
    return {"answer": answer}

# ==================== 节点4：计算器处理 ====================
def calculator_node(state: AgentState):
    """处理数学计算"""
    question = state["question"]
    
    # 让 DeepSeek 提取数学表达式
    prompt = f"""从以下问题中提取数学表达式，只返回表达式本身，不要解释。
如果问题不是数学计算，返回"None"。

问题：{question}
表达式："""
    
    expr = call_deepseek(prompt).strip().lower()
    
    if expr == "none" or not expr:
        return {"answer": "这不是一个数学计算问题，请尝试其他问题。"}
    
    # 允许的安全函数
    allowed_names = {
        "sqrt": math.sqrt,
        "pi": math.pi,
        "e": math.e,
        "abs": abs,
        "pow": pow
    }
    
    try:
        # 安全计算
        result = eval(expr, {"__builtins__": {}}, allowed_names)
        answer = f"计算结果：{expr} = {result}"
        print(f"  [计算器] {expr} = {result}")
    except Exception as e:
        answer = f"计算错误：{expr} 无法计算。请确保表达式正确。"
        print(f"  [计算器错误] {e}")
    
    return {"answer": answer}

# ==================== 路由函数 ====================
def route_by_intent(state: AgentState):
    """根据意图决定下一个节点"""
    if state["intent"] == "knowledge":
        return "knowledge"
    elif state["intent"] == "data":
        return "sql"
    else:
        return "calculator"

# ==================== 构建图 ====================
builder = StateGraph(AgentState)

# 添加节点
builder.add_node("classify", classify_node)
builder.add_node("knowledge", knowledge_node)
builder.add_node("sql", sql_node)
builder.add_node("calculator", calculator_node)

# 设置入口
builder.set_entry_point("classify")

# 添加条件边
builder.add_conditional_edges("classify", route_by_intent, {
    "knowledge": "knowledge",
    "sql": "sql",
    "calculator": "calculator"
})

# 添加结束边
builder.add_edge("knowledge", END)
builder.add_edge("sql", END)
builder.add_edge("calculator", END)

# 编译图
graph = builder.compile()

# ==================== 运行 ====================
if __name__ == "__main__":
    print("=" * 50)
    print("LangGraph 智能体 (知识库 + SQL + 计算器)")
    print("=" * 50)
    
    while True:
        question = input("\n请输入问题（输入 q 退出）：")
        if question.lower() == 'q':
            break
        
        print("\n正在处理...")
        
        initial_state = {
            "question": question,
            "intent": "",
            "answer": ""
        }
        
        result = graph.invoke(initial_state)
        
        print(f"\n答案：{result['answer']}")
        print("-" * 50)
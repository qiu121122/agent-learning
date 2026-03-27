import chromadb

# 创建客户端（使用本地持久化存储）
client = chromadb.PersistentClient(path="./chroma_data")

# 创建或获取集合（类似数据库的表）
collection = client.get_or_create_collection("test_collection")

# 添加文档（自动向量化）
collection.add(
    documents=["广州是广东省的省会", "AI Agent 是智能体程序", "Python 是一门编程语言"],
    metadatas=[{"source": "doc1"}, {"source": "doc2"}, {"source": "doc3"}],
    ids=["id1", "id2", "id3"]
)

# 检索相似文档
results = collection.query(
    query_texts=["广州的省会是哪里"],
    n_results=2
)

print("检索结果：")
print(results)
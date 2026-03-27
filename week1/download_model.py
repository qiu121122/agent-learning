from sentence_transformers import SentenceTransformer

print("正在下载模型...")
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
print("模型下载完成！")

# 测试一下
sentences = ["广州是广东省的省会", "AI Agent 是智能体程序"]
embeddings = model.encode(sentences)
print(f"向量维度: {len(embeddings[0])}")
print("模型可用！")
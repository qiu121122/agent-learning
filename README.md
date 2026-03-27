# AI Agent 学习项目

这个仓库记录了我学习 AI Agent 开发的实践过程。

## 项目目标
- 掌握 RAG（检索增强生成）技术
- 熟悉 Agent 开发框架（LangGraph）
- 完成一个可部署的多工具智能体

## 当前进度
- [x] 腾讯云 LKE 跑通 RAG
- [x] Python 调用 DeepSeek API
- [x] 本地 RAG 实现（Chroma + DeepSeek）
- [x] SQL Agent（Text-to-SQL）
- [x] 混合智能体（RAG + SQL + 意图判断）
- [x] LangGraph 多工具智能体（知识库 + SQL + 计算器）
- [ ] 服务化部署（FastAPI）

## 目录结构
agent-learning/
├── week1/
│ ├── test_api.py # DeepSeek API 调用
│ ├── local_rag.py # RAG 问答
│ ├── sql_agent.py # SQL Agent
│ ├── hybrid_agent.py # 混合智能体（if-else 版本）
│ ├── langgraph_agent.py # LangGraph 智能体（正式版）
│ ├── create_db.py # SQLite 数据库
│ ├── chroma_demo.py # Chroma 向量检索测试
│ ├── download_model.py # 下载 embedding 模型
│ └── .env # API Key（不上传）
├── 学习日志.md
└── README.md


## 技术栈
- Python 3.13
- DeepSeek API（大模型）
- Chroma（向量数据库）
- SQLite（业务数据库）
- LangGraph（Agent 框架）

## 智能体能力
当前智能体（`langgraph_agent.py`）支持三种问题：
1. **知识类** → RAG 检索文档回答
2. **数据类** → 生成 SQL 查询数据库
3. **计算类** → 数学计算

示例：
- “什么是 AI Agent？” → 知识类
- “笔记本卖了多少？” → 数据类
- “25 * 4 等于多少？” → 计算类

## 运行方式
```bash
cd week1
python langgraph_agent.py

下一步计划
增加联网搜索工具

支持多步推理（先查数据，再对比）

用 FastAPI 封装成服务

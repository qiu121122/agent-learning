import sqlite3

conn = sqlite3.connect("sales.db")
cursor = conn.cursor()

# 先删除旧表（重新开始）
cursor.execute("DROP TABLE IF EXISTS sales")

# 创建销售表
cursor.execute('''
CREATE TABLE sales (
    id INTEGER PRIMARY KEY,
    product TEXT,
    amount INTEGER,
    date TEXT
)
''')

# 插入更多数据
sales_data = [
    ("笔记本", 30, "2024-03-01"),
    ("鼠标", 50, "2024-03-02"),
    ("键盘", 20, "2024-03-03"),
    ("笔记本", 40, "2024-03-04"),
    ("鼠标", 60, "2024-03-05"),
    ("笔记本", 25, "2024-03-06"),
    ("鼠标", 45, "2024-03-07"),
    ("键盘", 35, "2024-03-08"),
]

cursor.executemany("INSERT INTO sales (product, amount, date) VALUES (?, ?, ?)", sales_data)

conn.commit()
conn.close()

print("数据库重建成功！")
print("数据统计：")
print("笔记本: 30+40+25 = 95")
print("鼠标: 50+60+45 = 155")
print("键盘: 20+35 = 55")
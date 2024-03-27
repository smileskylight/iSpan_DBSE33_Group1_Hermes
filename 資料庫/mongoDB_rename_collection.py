from pymongo import MongoClient

# 连接到MongoDB
client = MongoClient('mongodb://localhost:27017/')

# 选择数据库和集合
db = client['your_database_name']
old_collection_name = 'old_collection_name'
new_collection_name = 'new_collection_name'

# 重命名集合
db[old_collection_name].rename(new_collection_name)

print("Collection renamed successfully.")

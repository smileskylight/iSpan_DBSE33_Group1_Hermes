import pandas as pd
import pymongo
import json

# 读取 JSON 文件并转换为 DataFrame
with open('所有地點.txt', 'r', encoding='utf-8') as clocation:
    lines = clocation.readlines()
    for line in lines:
        line = line.strip() 
        with open(f'{line}.json', 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            # 连接到云端数据库
            client = pymongo.MongoClient("mongodb+srv://root:Anny12345!@cluster0.sbvqogz.mongodb.net/?retryWrites=true&w=majority")
            db = client.Taiwan_travel
            collection = db.data

            # 将整行数据插入数据库
            for row in data:
                collection.insert_one(row)

            print('数据建立成功')

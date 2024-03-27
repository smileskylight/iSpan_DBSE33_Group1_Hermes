import pymongo
import json

# 连接 MongoDB
client = pymongo.MongoClient("mongodb+srv://root:Anny12345!@cluster0.sbvqogz.mongodb.net/?retryWrites=true&w=majority")
db = client.test

# 读取 TXT 文件并将内容添加到 MongoDB
txt_file = 'your_file.txt'  # 替换为您的 TXT 文件名称

# 读取 TXT 文件
with open(txt_file, 'r', encoding='utf-8') as f:
    for line in f:
        # 去除换行符和空格
        json_filename = line.strip() + '.json'
        
        # 读取 JSON 文件
        with open(json_filename, 'r', encoding='utf-8') as json_data:
            json_content = json.load(json_data)
        
        # 遍历 JSON 中的每个字典
        for item in json_content:
            # 檢查字典中是否存在與 TXT 文件名稱相匹配的键值
            if "景點名稱" in item and item["景點名稱"] == line.strip():
                # 读取 TXT 文件内容
                with open(line.strip(), 'r', encoding='utf-8') as txt_data:
                    comment = txt_data.read()
                
                # 合併
                item["評論"] = comment  # 將評論加進去
                
                # 更新
                collection = db[json_filename]
                collection.replace_one({"景點名稱": line.strip()}, item, upsert=True)  # 使用 upsert=True 进行插入或更新操作

                print(f"数据成功合并和插入到 {json_filename}")

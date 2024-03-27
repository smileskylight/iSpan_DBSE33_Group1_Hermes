import json
import os

import mysql.connector  # pip install mysql-connector-python
from dotenv import load_dotenv  # pip install python-dotenv

import pymysql

# 連接到 MySQL 資料庫
load_dotenv()
conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=int(os.getenv("DB_PORT")),
    database=os.getenv("DATABASE"),
)


cursor = conn.cursor()
"""
# 創建數據庫

create_database_query = f"CREATE DATABASE {database}"
cursor.execute(create_database_query)
conn.commit()

# 資料庫
use_database_query = f"SHOW DATABASES"
cursor.execute(use_database_query)
conn.commit()

# 切換到 'tra_group' 資料庫
use_database_query = f"USE {database}"
cursor.execute(use_database_query)
conn.commit()
"""

# 建立表格
create_table_query = """
CREATE TABLE IF NOT EXISTS Tra_group_table_test2(
Attractions	BLOB,
Address	varchar(100),
City varchar(50),
District varchar(50),
Google_comment_web TEXT,
Star_counts varchar(50),
Opentime TEXT,
Comment_count varchar(50),
NS varchar(50),
WE varchar(50),
Tag TEXT,
5star int,
4star int,
3star int,
2star int,
1star int,
Mon_open varchar(50),
Mon_close varchar(50),
Tue_open varchar(50),
Tue_close varchar(50),
Wed_open varchar(50),
Wed_close varchar(50),
Thu_open varchar(50),
Thu_close varchar(50),
Fri_open varchar(50),
Fri_close varchar(50),
Sat_open varchar(50),
Sat_close varchar(50),
Sun_open varchar(50),
Sun_close varchar(50),
Comment BLOB,
Group_ya varchar(50)
)
"""
cursor.execute(create_table_query)
conn.commit()

# 導入多個 JSON 檔案中的數據到表格中
# json_folder = "/home/bigred/opendata/tra_group/split_group/"
# for filename in os.listdir(json_folder):
# if filename.endswith("3_ENG_v4.json.json"):
# filepath = os.path.join(json_folder, filename)
filepath = "/home/bigred/opendata/tra_group/split_group/kmeams_3_ENG_v4.json"
with open(filepath, "r", encoding="utf-8") as file:
    data = json.load(file)

for item in data:
    # 根據 JSON 檔案的格式，將數據插入到表格中
    insert_query = """
            INSERT INTO Tra_group_table (Attractions, Address, City, District, Google_comment_web, Star_counts, Opentime, Comment_count, NS, WE, Tag, 5star, 4star, 3star, 2star, 1star, Mon_open, Mon_close, Tue_open, Tue_close, Wed_open, Wed_close, Thu_open, Thu_close, Fri_open, Fri_close, Sat_open, Sat_close, Sun_open, Sun_close, Comment, Group_ya)
            VALUES (%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s)
            """
    values = (
        item["Attractions"],
        item["Address"],
        item["City"],
        item["District"],
        item["Google_comment_web"],
        item["Star_counts"],
        item["Opentime"],
        item["Comment_count"],
        item["NS"],
        item["WE"],
        item["Tag"],
        item["5star"],
        item["4star"],
        item["3star"],
        item["2star"],
        item["1star"],
        item["Mon_open"],
        item["Mon_close"],
        item["Tue_open"],
        item["Tue_close"],
        item["Wed_open"],
        item["Wed_close"],
        item["Thu_open"],
        item["Thu_close"],
        item["Fri_open"],
        item["Fri_close"],
        item["Sat_open"],
        item["Sat_close"],
        item["Sun_open"],
        item["Sun_close"],
        item["Comment"],
        item["Group"],
    )
    cursor.execute(insert_query, values)


conn.commit()

# 關閉連接
cursor.close()
conn.close()

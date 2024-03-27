import glob
import json
import os

# 讀取一個python template, 替換特定字, 生成新的python檔

# template python
template = "./02_table_data.py"

# json folder
json_path = "./*json"

# 指定新的 py 檔案路徑
output_json_path = "./py"

city_json = glob.glob(json_path)
for c in city_json:
    file_name = os.path.basename(c).split("/")[-1].split(".")[0].split("_")[0]
    # print(file_name)
    print(c)
    with open(template, "r", encoding="utf-8") as file:
        # data = file.readlines()
        data = file.read()
        new_data = data.replace("_INPUT_", c)
        print(new_data)

    with open(
        output_json_path + "/" + file_name + "_table_data.py", "w", encoding="utf-8"
    ) as f:
        f.write(new_data)

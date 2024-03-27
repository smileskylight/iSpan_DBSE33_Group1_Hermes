import glob
import json
import os

# input all.json
input_file = "./南投縣.json"


with open(input_file, "r", encoding="utf-8") as file:
    data = json.load(file)
    all_list = []
    for dict in data:
        all_list.append(dict["景點名稱"])


# input comment directory
# dir = "./comment/南投縣/*.txt"
comment_files = glob.glob(dir)
comment_path = dir.split("*")[0]
comment_list = []
for f in comment_files:
    file_name = os.path.basename(f).split(".")[0]
    comment_list.append(file_name)


# all.json check comment_files
filtered_data = []
for n, j in enumerate(all_list):
    if j in comment_list:
        with open(comment_path + j + ".txt", "r", encoding="utf-8") as j_file:
            content = j_file.read()
            if content.strip() == "[]":
                print(f"'{j}'的內容為 '[]'")
                # 將 data[n] 加入 filtered_data，後來發現內容[]是真的沒有評論，先關閉
                # filtered_data.append(data[n])
            else:
                continue
    else:
        filtered_data.append(data[n])
        print(f"'{j}'沒有檔案")
# print(filtered_data)

# 指定新的 JSON 檔案路徑
output_json_path = "./merged/filtered_data.json"

# 將 filtered_data 寫入新的 JSON 檔案
with open(output_json_path, "w", encoding="utf-8") as output_file:
    json.dump(filtered_data, output_file, indent=2, ensure_ascii=False)

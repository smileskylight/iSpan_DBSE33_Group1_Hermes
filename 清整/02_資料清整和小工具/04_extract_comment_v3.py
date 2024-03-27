import glob
import json
import os

# input json folder
file_path = "../05_分群/kmeans_split/split/*.json"
# 指定新的 JSON 檔案folder
output_folder = "./only_comment"

group_json = glob.glob(file_path)
# print(city_json)

for c in group_json:
    with open(c, "r", encoding="utf-8") as file:
        file_name = c.split("/")[-1].split("\\")[-1].split(".")[0]
        data = json.load(file)
        txt_content = ""
        for i, line in enumerate(data):
            if "5 顆星" in line["評論"]:
                if i % 500 == 1:
                    # print(line["評論"])
                    txt_content += line["評論"] + "\n"

    output_file_path = output_folder + "/" + file_name + "_only評論v3.txt"
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        output_file.write(txt_content)

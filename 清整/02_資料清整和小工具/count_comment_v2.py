import glob
import json
import os

# 使用範例
input_file = "./南投縣.json"
comment_dir = "./comment/南投縣/*.txt"
output_json_path = "./merged/filtered_data.json"


def filter_data(input_file, comment_dir, output_json_path):
    with open(input_file, "r", encoding="utf-8") as file:
        data = json.load(file)
        all_list = [item["景點名稱"] for item in data]

    comment_files = glob.glob(comment_dir)
    comment_path = comment_dir.split("*")[0]
    comment_list = [os.path.basename(f).split(".")[0] for f in comment_files]

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

    with open(output_json_path, "w", encoding="utf-8") as output_file:
        json.dump(filtered_data, output_file, indent=2, ensure_ascii=False)


filter_data(input_file, comment_dir, output_json_path)

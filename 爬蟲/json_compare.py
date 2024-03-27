import os
import glob
import json

# input final.json
newone = input("請輸入新檔案的絕對位置")
input_file = rf"{newone}"
with open(input_file, 'r', encoding='utf-8') as file:
    data = json.load(file)
    all_list = []
    for dict in data:      
        all_list.append(dict["景點名稱"])
  

#input previous.json
oldone = input("請輸入舊檔案的絕對位置")
input_file2 = rf"{oldone}"
with open(input_file2, 'r', encoding='utf-8') as file2:
    data2 = json.load(file2)
    pre_list = []
    for dict2 in data2:      
        pre_list.append(dict2["景點名稱"])


# find lack place
filtered_data = []
count = 0
for n, j in enumerate(all_list):
    if j in pre_list:
        continue
    else:
        print(j)
        filtered_data.append(data[n])
        count += 1
print(f"##新json比舊json少了{count}個地點評論")        
# print(filtered_data)

#指定新的 JSON 檔案路徑
output_json_path = "./merged/diff_place.json"

# 將 filtered_data 寫入新的 JSON 檔案
with open(output_json_path, 'w', encoding='utf-8') as output_file:
    json.dump(filtered_data, output_file, indent=2, ensure_ascii=False)
import os
import glob

list_path = "要抓的地點1.txt"
with open(list_path, 'r', encoding='utf-8') as file:
    data = file.readlines() 
    all_file_list = []
    for i in data:
          all_file_list.append(i.strip())
    # print(all_file_list)


folder_path = "./*json"
json_files = []
# 使用 glob 模組來匹配檔案
matching_files = glob.glob(folder_path)
json_files = []
for file in matching_files:
    file_name = os.path.basename(file).split(".")[0]
    json_files.append(file_name)

count = 0
for f in all_file_list:
    # print(file_name)
    if f in json_files:
        count += 1
    else:
         print(f)
         with open('要抓的地點.txt', 'a', encoding='utf-8') as files:
            files.write(f'{f}\n')
print(f'目前資料夾內json檔案有{count}個')


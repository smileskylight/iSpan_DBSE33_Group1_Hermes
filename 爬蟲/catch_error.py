import json

import os


path = "./rawdata"  # 文件夾目錄
files = os.listdir(path)  # 得到文件夾下的所有文件名稱

with open("錯誤訊息.txt", 'w', encoding='utf-8') as error_file, open("錯誤地點.txt", 'w', encoding='utf-8') as error_location:
    for file in files:  # 遍歷文件夾
        position = os.path.join(path, file)  # 構造絕對路徑
        folder_name = position.split("\\")[1].split(".")[0]
        with open(position, "r", encoding='utf-8') as file:  # 打開文件
            data = json.load(file)  # 讀取文件
            # 從JSON數據中提取景點名稱和評論網址
            errors = [(item["景點名稱"], item["地址"], item["tag"], item["營業時間"]) for item in data]
            for error in errors:
                if any("錯誤" in item for item in error):
                    print(f'{position} 的 {error} 有錯誤')
                    error_file.write(f'{position} 的 {error} 有錯誤\n')
                    error_location.write(folder_name + '\n')


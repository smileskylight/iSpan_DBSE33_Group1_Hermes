import json
import re
import os


# ---清 none ---
def should_remove_area(item):
    return (
        item.get("5星評論數", 0) == 0 or
        item.get("評論數量", "None") == "None" 
    )

folder_path = './rawdata'
rawdata_file_names = [f for f in os.listdir(folder_path) if f.endswith('.json')]

target_folder = f'./notnone'
if not os.path.exists(target_folder):
    os.makedirs(target_folder)

# 讀檔案
for file_name in rawdata_file_names:
    try:
        with open(os.path.join(folder_path, file_name), 'r', encoding='utf-8') as file:
            data = json.load(file)
    except Exception as e:
        print(f"Error loading {file_name}: {e}")
        continue  # 如果檔案有問題，跳到下一個迴圈

    filtered_data = [item for item in data if not should_remove_area(item)]

# ---分欄位 ---

    # 目標資料夾，用於存放處理過的 JSON 檔案
    target_folder = './splited'
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
        
    # 初始化結果列表
    result_list = []
    
    for item in filtered_data:

        title = item.get("景點名稱","")
        # 清理髒東西
        filthy_list = ["/", "\\", "|", "'", "*"]
        for filthy in filthy_list:
            if filthy in title :
                title = title.replace(filthy, " ")
        # 限制長度
        if len(title) > 20:
            title = title[:20]
        city = ""
        area = ""
        address = item.get("地址", "")
        reg = r'([0-9]*)(\S+縣|\S+市)(\S+市|\S+鎮|\S+區|\S+鄉)'
        match = re.search(reg, address)
        if match:
            city = match.group(2)
            area = match.group(3)

        # 取得景點營業時間
        business_hours = item.get("營業時間", "")

        item_dic = {
            "景點名稱": title,
            "地址": item.get("地址", ""),
            "縣市": city,
            "鄉鎮區": area,
            "Google評論網址": item.get("Google評論網址", ""),
            "星數": item.get("星數", ""),
            "營業時間": item.get("營業時間", ""),
            "評論數量": item.get("評論數量", ""),
            "緯度": item.get("緯度", ""),
            "經度": item.get("經度", ""),
            "tag": item.get("tag", ""),
            "5星評論數": item.get("5星評論數", ""),
            "4星評論數": item.get("4星評論數", ""),
            "3星評論數": item.get("3星評論數", ""),
            "2星評論數": item.get("2星評論數", ""),
            "1星評論數": item.get("1星評論數", ""),
            "星期一開始營業時間": "00",
            "星期一結束營業時間": "00",
            "星期二開始營業時間": "00",
            "星期二結束營業時間": "00",
            "星期三開始營業時間": "00",
            "星期三結束營業時間": "00",
            "星期四開始營業時間": "00",
            "星期四結束營業時間": "00",
            "星期五開始營業時間": "00",
            "星期五結束營業時間": "00",
            "星期六開始營業時間": "00",
            "星期六結束營業時間": "00",
            "星期日開始營業時間": "00",
            "星期日結束營業時間": "00"
        }

        # 初始化結果的起始和結束時間
        start_time = "00"
        end_time = "00"

        # 如果有營業時間
        if business_hours:
            business_hours = business_hours.replace("隱藏本週營業時間", "")
            if "休息" not in business_hours:
                time_periods = business_hours.split(";")
                for time_period in time_periods:
                    if "沒有顯示" in time_period:
                        # 24 小時營業的情況
                        item_dic["星期一開始營業時間"] = "00"
                        item_dic["星期一結束營業時間"] = "24"
                        item_dic["星期二開始營業時間"] = "00"
                        item_dic["星期二結束營業時間"] = "24"
                        item_dic["星期三開始營業時間"] = "00"
                        item_dic["星期三結束營業時間"] = "24"
                        item_dic["星期四開始營業時間"] = "00"
                        item_dic["星期四結束營業時間"] = "24"
                        item_dic["星期五開始營業時間"] = "00"
                        item_dic["星期五結束營業時間"] = "24"
                        item_dic["星期六開始營業時間"] = "00"
                        item_dic["星期六結束營業時間"] = "24"
                        item_dic["星期日開始營業時間"] = "00"
                        item_dic["星期日結束營業時間"] = "24"

                    else:
                        # 拆分星期和時間段
                        if "、" in time_period:
                            day, hours = time_period.split("、", 1)
                            day = day.strip()

                        if "24 小時營業" in hours:
                            # 24 小時營業的情況
                            start_time = "00"
                            end_time = "24"
                        else:
                            # 拆分開始和結束時間
                            if "到" in hours:
                                start, end = hours.split("到", 1)
                                if "到" in end:
                                    tem_01, tem_02 = hours.split("、", 1)
                                    tem_01, end = tem_02.split("到", 1)
                                start_h, start_m = start.split(":", 1)
                                end_h, end_m = end.split(":", 1)

                                start_time = start_h
                                end_time = end_h

                        # 處理每個星期的時間
                        item_dic[f"{day}開始營業時間"] = start_time
                        item_dic[f"{day}結束營業時間"] = end_time

                # 將每個景點的資料加入結果列表
                result_list.append(item_dic)

    # 將結果字典和輸入資料寫入新的 JSON 檔案
    file_name_clear = os.path.join(target_folder, f'{file_name.replace(".json", "")}.json')

    with open(file_name_clear, 'w', encoding='utf-8') as output_file:
        json.dump(result_list, output_file, indent=2, ensure_ascii=False)

# ---合併縣市 ---

city_list = ['臺北市', '新北市', '桃園市', '臺中市', '臺南市', '高雄市', '基隆市', '新竹市', '嘉義市', '新竹縣', '苗栗縣', '彰化縣', '南投縣', '雲林縣', '嘉義縣', '屏東縣', '宜蘭縣', '花蓮縣', '臺東縣', '澎湖縣', '金門縣', '連江縣']

for city_name in city_list:

    filtered_datas = []
    visited_attractions = set()
    result_list = []
    
    # 原始 JSON 檔案所在的資料夾
    folder_path = './splited'
    file_names = [f for f in os.listdir(folder_path) if f.endswith('.json')]
    
    # 目標資料夾，用於存放處理過的 JSON 檔案
    target_folder = './merged'
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    # 讀取各 JSON 檔案資料
    for file_name in file_names:
        if city_name in file_name:
            try:
                with open(os.path.join(folder_path, file_name), 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    # get all items and append to filtered_datas
                    filtered_datas.extend(data)
            except Exception as e:
                print(f"Error loading {file_name}: {e}")
                continue  # Skip to the next iteration if there's an issue with the file

    # 確認是否重複 以及是否在同一縣市
    for data in filtered_datas:
        attraction_name = data.get("景點名稱", "")
        address_city = data.get("地址", "")
        address_checker = city_name
        if "臺" in city_name:
            address_checker = f"台{city_name[1]}"
        if address_checker in address_city:
            if attraction_name and attraction_name not in visited_attractions:
                result_list.append(data)
                visited_attractions.add(attraction_name)

    if len(result_list) != 0:
        # 將結果列表寫入新的 JSON 檔案
        file_name_output = os.path.join(target_folder, f'{city_name}.json')
        with open(file_name_output, 'w', encoding='utf-8') as output_file:
            json.dump(result_list, output_file, indent=2, ensure_ascii=False)

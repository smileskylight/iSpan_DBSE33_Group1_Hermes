import json
import os
import re

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


city_list = [
        "臺北市",
        "新北市",
        "桃園市",
        "臺中市",
        "臺南市",
        "高雄市",
        "基隆市",
        "新竹市",
        "嘉義市",
        "新竹縣",
        "苗栗縣",
        "彰化縣",
        "南投縣",
        "雲林縣",
        "嘉義縣",
        "屏東縣",
        "宜蘭縣",
        "花蓮縣",
        "臺東縣",
        "澎湖縣",
        "金門縣",
        "連江縣",
    ]

# 檢查是否應該移除景點
def should_remove_attraction(attraction):
    return (
        attraction.get("5星評論數", 0) == 0
        or attraction.get("評論數量", "None") == "None"
    )


def splited_colum_data(filtered_data):
    result_list = []
    for attraction in filtered_data:
        title = attraction.get("景點名稱", "")
        title = (
            title.replace("/", " ")
            .replace("\\", " ")
            .replace("|", " ")
            .replace("'", " ")
            .replace("*", " ")
            .replace("｜", " ")
            .replace("／", " ")
            .replace("＼", " ")
        )
        title = title[:20] if len(title) > 20 else title

        city = ""
        area = ""
        address = attraction.get("地址", "")
        reg = r"([0-9]*)(\S+縣|\S+市)(\S+市|\S+鎮|\S+區|\S+鄉)"
        match = re.match(reg, address)
        if match:
            city = match.group(2)
            area = match.group(3)
            if area and (
                area.count("鄉")
                + area.count("區")
                + area.count("鎮")
                + area.count("市")
                >= 2
            ):
                area = re.search(r"(.*?(?:鄉|區|鎮|市)).*", area).group(1)

        business_hours = attraction.get("營業時間", "")
        attraction_dic = {
            "景點名稱": title,
            "地址": attraction.get("地址", ""),
            "縣市": city,
            "鄉鎮區": area,
            "Google評論網址": attraction.get("Google評論網址", ""),
            "星數": attraction.get("星數", ""),
            "營業時間": attraction.get("營業時間", ""),
            "評論數量": attraction.get("評論數量", ""),
            "緯度": attraction.get("緯度", ""),
            "經度": attraction.get("經度", ""),
            "tag": attraction.get("tag", ""),
            "5星評論數": attraction.get("5星評論數", ""),
            "4星評論數": attraction.get("4星評論數", ""),
            "3星評論數": attraction.get("3星評論數", ""),
            "2星評論數": attraction.get("2星評論數", ""),
            "1星評論數": attraction.get("1星評論數", ""),
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
            "星期日結束營業時間": "00",
        }

        start_time = "00"
        end_time = "00"

        if business_hours:
            business_hours = business_hours.replace("隱藏本週營業時間", "").replace(
                "、營業時間可能不同", ""
            )
            if "休息" not in business_hours:
                time_periods = business_hours.split(";")
                for time_period in time_periods:
                    if "沒有顯示" in time_period or "錯誤" in time_period:
                        attraction_dic["星期一結束營業時間"] = "24"
                        attraction_dic["星期二結束營業時間"] = "24"
                    else:
                        if "、" in time_period:
                            day, hours = time_period.split("、", 1)
                            day = day.strip()

                        if "24 小時營業" in hours:
                            start_time = "00"
                            end_time = "24"
                        else:
                            if "到" in hours:
                                start, end = hours.split("到", 1)
                                if "到" in end:
                                    tem_01, tem_02 = hours.split("、", 1)
                                    tem_01, end = tem_02.split("到", 1)
                                start_h, start_m = start.split(":", 1)
                                end_h, end_m = end.split(":", 1)

                                start_time = start_h
                                end_time = end_h

                        attraction_dic[f"{day}開始營業時間"] = start_time
                        attraction_dic[f"{day}結束營業時間"] = end_time

                result_list.append(attraction_dic)

    return result_list


def splited_data(rawdata_folder = "./rawdata" , target_folder = "./splited"):
    
    rawdata_files = [f for f in os.listdir(rawdata_folder) if f.endswith(".json")]

    """
    分割縣市、地區及每日營業時間
    """
    for file_name in rawdata_files:
        try:
            with open(
                os.path.join(rawdata_folder, file_name), "r", encoding="utf-8"
            ) as file:
                data = json.load(file)
        except Exception as e:
            print(f"Error loading {file_name}: {e}")
            continue

        filtered_data = [
            attraction for attraction in data if not should_remove_attraction(attraction)
        ]

        
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)

        result_list = splited_colum_data(filtered_data)

        file_name_clear = os.path.join(
            target_folder, f'{file_name.replace(".json", "")}.json'
        )

        with open(file_name_clear, "w", encoding="utf-8") as output_file:
            json.dump(result_list, output_file, indent=2, ensure_ascii=False)


def chk_repeat(city_name , file_names):
    filtered_attractions = []
    visited_attractions = []
    result_list = []

    for file_name in file_names:
        if city_name in file_name:
            try:
                with open(
                    os.path.join(folder_path, file_name), "r", encoding="utf-8"
                ) as file:
                    data = json.load(file)
                    filtered_attractions.extend(data)
            except Exception as e:
                print(f"Error loading {file_name}: {e}")
                continue

    for data in filtered_attractions:
        attraction_name = data.get("景點名稱", "")
        address_city = data.get("地址", "")
        
        if "臺" in city_name:
            city_name = f"台{city_name[1]}"
        if city_name in address_city:
            if attraction_name and attraction_name not in visited_attractions:
                result_list.append(data)
                visited_attractions.append(attraction_name)

    return result_list


def merged_city():
    # 合併特定城市的景點資料
    

    for city_name in city_list:
        

        folder_path = "./splited"
        file_names = [f for f in os.listdir(folder_path) if f.endswith(".json")]

        target_folder = "./merged"
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)

        result_list = chk_repeat(city_name , file_names)

        if len(result_list) != 0:
            file_name_output = os.path.join(target_folder, f"{city_name}.json")
            with open(file_name_output, "w", encoding="utf-8") as output_file:
                json.dump(result_list, output_file, indent=2, ensure_ascii=False)


def chk_repeat_att(folder_path = "./merged", target_folder = "./chk_att"):
    """
    檢查重複的景點
    """
    all_attractions = []
    visited_attractions = []
    recurring_set = []
    recurring_list = []


    file_names = [f for f in os.listdir(folder_path) if f.endswith(".json")]


    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    for file_name in file_names:
        try:
            with open(os.path.join(folder_path, file_name), "r", encoding="utf-8") as file:
                data = json.load(file)

        except Exception as e:
            print(f"Error loading {file_name}: {e}")
            continue

        for item in data:
            attraction_name = item.get("景點名稱", "")
            attraction_url = item.get("Google評論網址", "")

            if attraction_url not in visited_attractions:
                visited_attractions.append(attraction_url)
                all_attractions.append(item)
            elif attraction_url in visited_attractions:
                recurring = f"{file_name} => {attraction_name}"
                recurring_list.append(recurring)
                if attraction_url not in recurring_set:
                    recurring_set.append(attraction_url)

    if len(recurring_list) != 0:
        file_name_output = os.path.join(target_folder, "recurring_attraction.txt")
        with open(file_name_output, "w", encoding="utf-8") as output_file:
            json.dump(recurring_list, output_file, indent=2, ensure_ascii=False)

    if len(recurring_set) != 0:
        file_name_output = os.path.join(target_folder, "recurring_attraction_url.txt")
        with open(file_name_output, "w", encoding="utf-8") as output_file:
            json.dump(recurring_set, output_file, indent=2, ensure_ascii=False)

    if len(all_attractions) != 0:
        file_name_output = os.path.join(target_folder, "taiwan.json")
        with open(file_name_output, "w", encoding="utf-8") as output_file:
            json.dump(all_attractions, output_file, indent=2, ensure_ascii=False)


def get_address(url):
    """
    校正地址資料
    """
    ua = UserAgent()
    my_header = {"User-Agent": ua.random}

    try:
        response = requests.get(url, headers=my_header)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")
        location = soup.find("meta", itemprop="name")["content"]
        return location
    except (requests.RequestException, KeyError, TypeError) as e:
        print(f"Error fetching address for {url}: {e}")
        return None


def correct_data(folder_path = "./chk_att", taiwan_json = "taiwan.json", url_file = "recurring_attraction_url.txt", target_folder = "./chk_att"):
    try:
        with open(
            os.path.join(folder_path, taiwan_json), "r", encoding="utf-8"
        ) as file:
            taiwan_data = json.load(file)
        with open(
            os.path.join(folder_path, url_file), "r", encoding="utf-8"
        ) as url_list:
            url_list_str = url_list.read()
    except Exception as e:
        print(f"Error opening file: {e}")
        return

    taiwan = []

    for item in taiwan_data:
        attraction_url = item.get("Google評論網址", "")
        if attraction_url in url_list_str:
            addr = get_address(attraction_url)
            split_addr = addr.split(" · ", 1)
            if len(split_addr) == 2:
                _, addr = addr.split(" · ", 1)
            else:
                addr = split_addr[0]
            item["地址"] = addr
        taiwan.append(item)

    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    if taiwan:
        file_name_output = os.path.join(target_folder, "taiwan_correction.json")
        with open(file_name_output, "w", encoding="utf-8") as output_file:
            json.dump(taiwan, output_file, indent=2, ensure_ascii=False)


def del_lunar(file_names = "./chk_att/taiwan_correction.json", target_folder = "./clean"):
    

    target_folder = "./clean"
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    try:
        with open(file_names, "r", encoding="utf-8") as file:
            data = json.load(file)
    except Exception as e:
        print(f"Error loading {file_names}: {e}")

    for city_name in city_list:
        city_attraction_item = []
        for item in data:
            if city_name in item.get("地址", ""):
                attraction_item = {
                    key: value
                    for key, value in item.items()
                    if "新春" not in key and "除夕" not in key
                }
                city_attraction_item.append(attraction_item)

        file_name_output = os.path.join(target_folder, f"{city_name}.json")
        with open(file_name_output, "w", encoding="utf-8") as output_file:
            json.dump(city_attraction_item, output_file, indent=2, ensure_ascii=False)


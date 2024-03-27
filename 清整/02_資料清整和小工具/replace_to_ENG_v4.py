import glob
import json
import os

# input json folder
file_path = "../01_web_scraping/All/add_comment/*.json"
# 指定新的 JSON 檔案folder
output_folder = "../01_web_scraping/All/add_comment/ENG/"

city_name = {
    "台中市": "Taichung City",
    "台北市": "Taipei City",
    "台東縣": "Taitung County",
    "台南市": "Tainan City",
    "宜蘭縣": "Yilan County",
    "花蓮縣": "Hualien County",
    "金門縣": "Kinmen County",
    "南投縣": "Nantou County",
    "屏東縣": "Pingtung County",
    "苗栗縣": "Miaoli County",
    "桃園市": "Taoyuan City",
    "高雄市": "Kaohsiung City",
    "基隆市": "Keelung City",
    "連江縣": "Lienchiang County",
    "雲林縣": "Yunlin County",
    "新北市": "New Taipei City",
    "新竹市": "Hsinchu City",
    "新竹縣": "Hsinchu County",
    "嘉義市": "Chiayi City",
    "嘉義縣": "Chiayi County",
    "彰化縣": "Changhua County",
    "澎湖縣": "Penghu County",
    "": "",
}

city_json = glob.glob(file_path)
# print(city_json)

for c in city_json:
    with open(c, "r", encoding="utf-8") as file:
        file_name = c.split("/")[-1].split("\\")[-1].split(".")[0]
        data = json.load(file)
        ENG_json = []
        for line in data:
            ENG_dict = {}
            ENG_dict["Attractions"] = line["景點名稱"]
            ENG_dict["Address"] = line["地址"]
            # ENG_dict["City"] = city_name[line["縣市"]]
            ENG_dict["City"] = line["縣市"]
            ENG_dict["District"] = line["鄉鎮區"]
            ENG_dict["Google_comment_web"] = line["Google評論網址"]
            ENG_dict["Star_counts"] = line["星數"]
            ENG_dict["Opentime"] = line["營業時間"]
            ENG_dict["Comment_count"] = line["評論數量"]
            ENG_dict["NS"] = line["緯度"]
            ENG_dict["WE"] = line["經度"]
            ENG_dict["Tag"] = line["tag"]
            ENG_dict["5star"] = line["5星評論數"]
            ENG_dict["4star"] = line["4星評論數"]
            ENG_dict["3star"] = line["3星評論數"]
            ENG_dict["2star"] = line["2星評論數"]
            ENG_dict["1star"] = line["1星評論數"]
            ENG_dict["Mon_open"] = line["星期一開始營業時間"]
            ENG_dict["Mon_close"] = line["星期一結束營業時間"]
            ENG_dict["Tue_open"] = line["星期二開始營業時間"]
            ENG_dict["Tue_close"] = line["星期二結束營業時間"]
            ENG_dict["Wed_open"] = line["星期三開始營業時間"]
            ENG_dict["Wed_close"] = line["星期三結束營業時間"]
            ENG_dict["Thu_open"] = line["星期四開始營業時間"]
            ENG_dict["Thu_close"] = line["星期四結束營業時間"]
            ENG_dict["Fri_open"] = line["星期五開始營業時間"]
            ENG_dict["Fri_close"] = line["星期五結束營業時間"]
            ENG_dict["Sat_open"] = line["星期六開始營業時間"]
            ENG_dict["Sat_close"] = line["星期六結束營業時間"]
            ENG_dict["Sun_open"] = line["星期日開始營業時間"]
            ENG_dict["Sun_close"] = line["星期日結束營業時間"]
            ENG_dict["Comment"] = line["評論"]
            ENG_dict["Group"] = line["組別"]
            ENG_json.append(ENG_dict)
        # break
    # print(ENG_json)
    output_file_path = output_folder + file_name + "_ENG" + "_v4.json"
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        json.dump(ENG_json, output_file, ensure_ascii=False, indent=2)

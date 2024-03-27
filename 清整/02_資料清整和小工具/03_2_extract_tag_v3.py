import json

file_path = "../01_web_scraping/All/taiwan/taiwan_correction.json"
output_path = "../01_web_scraping/All/taiwan/"
# file_path = "./_INPUT_"
file_name = file_path.split("/")[-1].split(".")[0]
with open(file_path, "r", encoding="utf-8") as file:
    data = json.load(file)
    Tag_json = []
    count = 0
    for line in data:
        count += 1
        Tag_dict = {}
        Tag_dict["no"] = count
        Tag_dict["景點名稱"] = line["景點名稱"]
        Tag_dict["縣市"] = line["縣市"]
        Tag_dict["景點名稱_City"] = f'{line["景點名稱"]}_{line["縣市"]}'
        Tag_dict["星數"] = line["星數"]
        Tag_dict["Tag_all"] = line["tag"]
        # Tag_dict["組別"] = line["組別"]

        for t in line["tag"].split(","):
            dict_new = {}
            if t == "全部":
                pass
            else:

                Tag_dict["Tag"] = t
                dict_new.update(Tag_dict)
                Tag_json.append(dict_new)


output_file_path = output_path + "/" + file_name + "_tag_v3" + ".json"
# output_file_path = "./" + file_name + _OUTPUT_ + ".json"
with open(output_file_path, "w", encoding="utf-8") as output_file:
    json.dump(Tag_json, output_file, ensure_ascii=False, indent=2)

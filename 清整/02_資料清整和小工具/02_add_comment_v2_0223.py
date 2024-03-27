import glob
import json
import os

# input comment folder
comment_path = "./comment/"
# input json folder
# folder_path = "./縣市json/金門連江.json"
folder_path = "./縣市json/*json"
# 指定新的 JSON 檔案路徑
output_json_path = "./add_comment/"


def merge_comments(comment_path, folder_path, output_json_path):
    city_json = glob.glob(folder_path)

    # print(city_json)
    for c in city_json:
        json_list = []
        city_name = os.path.basename(c).split(".")[0]
        # print(city_name)
        with open(c, "r", encoding="utf-8") as city:
            location = json.load(city)
            for dict in location:
                name = dict["景點名稱"]
                comment_txt = glob.glob(comment_path + city_name + "/" + name + ".txt")
                # print(comment_txt)
                # IndexError: list index out of range
                try:
                    with open(comment_txt[0], "r", encoding="utf-8") as comment_file:
                        data = comment_file.readlines()
                        data_list = eval(data[0].strip())
                        # print(data_list)
                        if data_list == []:
                            dict["評論"] = ""
                            json_list.append(dict)
                        else:
                            for i in data_list:
                                # print(i, n)
                                dict_new = {}
                                dict["評論"] = i
                                dict["評論"] = dict["評論"].replace("\n", " ")
                                dict_new.update(dict)
                                json_list.append(dict_new)
                                # print(dict_new)
                except:
                    dict["評論"] = ""
                    json_list.append(dict)
                    print(f'{dict["景點名稱"]} 沒抓到評論的檔案')

        # 將 filtered_data 寫入新的 JSON 檔案
        with open(
            output_json_path + city_name + "_comment.json", "w", encoding="utf-8"
        ) as output_file:
            json.dump(json_list, output_file, indent=2, ensure_ascii=False)


merge_comments(comment_path, folder_path, output_json_path)

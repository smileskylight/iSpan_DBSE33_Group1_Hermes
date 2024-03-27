import glob
import json
import os

# input json folder
folder_path = "./亭安分群/group/*json"


def count_group(folder_path):
    group_json = glob.glob(folder_path)

    # print(group_json)
    for c in group_json:
        # group_name = os.path.basename(c).split(".")[0]
        # print(group_name)
        with open(c, "r", encoding="utf-8") as group:
            location = json.load(group)
            count = 0
            for dict in location:
                count += 1
            print(f"{c} 有{count}則評論")


count_group(folder_path)

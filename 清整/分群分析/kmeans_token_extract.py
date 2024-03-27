import json
import os
import re

import jieba
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

# 將群組檔案內的評論token後取出，分群後分為12個json檔

# folder_path = "./kmeans_split"
folder_path = "./group"
rawdata_file_names = [f for f in os.listdir(folder_path) if f.endswith(".json")]

# 指定新的 JSON 檔案folder
output_folder = "./token"


"""
def get_rawdata():
    folder_path = "./kmeans_split"
    result_list = []
    rawdata_file_names = [f for f in os.listdir(folder_path) if f.endswith(".json")]

    # 讀檔案
    for file_name in rawdata_file_names:
        try:
            with open(
                os.path.join(folder_path, file_name), "r", encoding="utf-8"
            ) as file:
                data = json.load(file)
        except Exception as e:
            print(f"Error loading {file_name}: {e}")
            continue  # 如果檔案有問題，跳到下一個迴圈

        for item in data:
            result_list.append(item)

    return result_list
"""


def stop_words():
    # 停用字文档的路径
    stopword_file_path = "./stopwords.txt"

    # 定义一个空列表用于存储停用词
    stop_words = []

    # 读取停用字文档并将其存储到 stopword 列表中
    with open(stopword_file_path, "r", encoding="utf-8") as file:
        for line in file:
            stop_words.append(line.strip())  # 去除每行末尾的换行符并添加到列表中

    return stop_words


# Jieba切字並清除停用字
def tokenize(comment):
    words = jieba.cut(comment)
    stop_words_list = stop_words()  # Rename the variable to avoid conflict
    # return " ".join(w for w in words if w not in stop_words_list)
    list_0 = [w for w in words if w not in stop_words_list]
    list = [i for i in list_0 if i.strip()]
    return list


for file_name in rawdata_file_names:
    print(file_name)
    try:
        with open(os.path.join(folder_path, file_name), "r", encoding="utf-8") as file:
            output_file_name = file_name.split(".")[0]
            data = json.load(file)
    except Exception as e:
        print(f"Error loading {file_name}: {e}")
        continue  # 如果檔案有問題，跳到下一個迴圈
    txt_content = "評論\n"
    comments = []
    for dict in data:
        comments.append(dict["評論"])
    tokenized_comments = [tokenize(comment) for comment in comments]
    # print(tokenized_comments)
    for i in tokenized_comments:
        for j in i:
            # print(j)
            reg = r"\D+"
            match_j1 = re.search(reg, j)

            if match_j1:
                match_j1_str = match_j1.group()
                reg2 = r"\w*"
                match_j = re.search(reg2, match_j1_str)
                if match_j:
                    txt_content += match_j.group() + "\n"
    # print(txt_content)
    output_file_path = output_folder + "/" + output_file_name + "_評論token.txt"
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        output_file.write(txt_content)

    # for t in tokenized_comments:
    # txt_content += t + "\n"

    # output_file_path = output_folder + "/" + output_file_name + "_評論token.txt"
    # with open(output_file_path, "w", encoding="utf-8") as output_file:
    #     output_file.write(txt_content)

# data = get_rawdata()
# print(data)


# 取出評論資料
"""
comments = [d["評論"] for d in data]
tokenized_comments = [tokenize(comment) for comment in comments]

print(tokenized_comments)
"""
# Doc2Vec轉向量
"""
documents = [
    TaggedDocument(doc.split(), [i]) for i, doc in enumerate(tokenized_comments)
]
model = Doc2Vec(documents, vector_size=100, window=2, min_count=1, workers=4)

vectors = [model.infer_vector(doc.words) for doc in documents]

# k-means聚類
k = 12
kmeans = KMeans(n_clusters=k, random_state=42)
clusters = kmeans.fit_predict(vectors)

# 將聚類結果新增到資料中
for i, d in enumerate(data):
    d["組別"] = str(clusters[i])

# 存成.json檔案
with open("test_kmeans.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
"""

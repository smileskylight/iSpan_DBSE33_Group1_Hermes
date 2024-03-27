from gensim.models import Doc2Vec, Word2Vec
from gensim.models.doc2vec import TaggedDocument
import jieba
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer
import json
import os

# 讀取原始資料
def get_rawdata():
    folder_path = "./test2"
    result_list = []
    rawdata_file_names = [f for f in os.listdir(folder_path) if f.endswith(".json")]

    # 讀取檔案
    for file_name in rawdata_file_names:
        try:
            with open(os.path.join(folder_path, file_name), "r", encoding="utf-8") as file:
                data = json.load(file)
                result_list.extend(data)
        except Exception as e:
            print(f"Error loading {file_name}: {e}")

    return result_list

# 準備數據
documents = get_rawdata()
df = pd.DataFrame(documents)

specific_comment_key = "評論"
specific_tag_key = "tag"
stopword_file_path = './stopwords.txt'
stop_words = []

# 讀取停用詞
with open(stopword_file_path, 'r', encoding='utf-8') as file:
    for line in file:
        stop_words.append(line.strip())

# 處理評論和標籤
comment_documents = []
tag_documents = []
label_encoder = LabelEncoder()
df['景點名稱_label'] = label_encoder.fit_transform(df['景點名稱'])

for document in documents:
    # if specific_comment_key in document and document[specific_comment_key] != '':
    #     words = jieba.lcut(document[specific_comment_key])
    #     filtered_words = [word for word in words if word.strip() not in stop_words]
    #     comment_documents.append(TaggedDocument(filtered_words, [len(comment_documents)]))
    # else:
    #     comment_documents.append(TaggedDocument([], [len(comment_documents)]))

    if specific_tag_key in document and document[specific_tag_key] != '':
        tags = document[specific_tag_key].split(",")
        filtered_tags = [tag.strip() for tag in tags if tag.strip() not in stop_words]
        tag_documents.append(filtered_tags)
    else:
        tag_documents.append([])

# 訓練 Doc2Vec 模型（處理評論）
# comment_model = Doc2Vec(vector_size=100, window=2, min_count=1, epochs=20)
# comment_model.build_vocab(comment_documents)
# comment_model.train(comment_documents, total_examples=comment_model.corpus_count, epochs=comment_model.epochs)
# comment_vectors = [comment_model.dv[i] for i in range(len(comment_documents))]

# 訓練 Word2Vec 模型
tag_model = Word2Vec(
    tag_documents, 
    vector_size=100,  
    window=2, 
    sg=0, 
    min_count=1,
    seed=42,
    epochs=20)

# 合併評論向量和標籤向量
df_combined = pd.concat([df['景點名稱_label'].astype(str), 
                         pd.DataFrame(tag_model.wv.vectors)], axis=1)

# Convert column names to strings
df_combined.columns = df_combined.columns.astype(str)

# 填充 NaN 值並標準化數據
imputer = SimpleImputer(strategy='mean')
scaler_combined = StandardScaler()
df_combined_filled = pd.DataFrame(imputer.fit_transform(df_combined), columns=df_combined.columns)
df_combined_scaled = scaler_combined.fit_transform(df_combined_filled)

# 定義 K-means 模型
def k_means(n_clusters, your_data):
    kmeans_model = KMeans(n_clusters=n_clusters, n_init=30, random_state=0)
    clusters = kmeans_model.fit_predict(your_data)

    # 將景點名稱和對應的聚類標籤存儲到一個字典中
    result_data = []
    for i, d in enumerate(documents):
        d["組別"] = str(clusters[i])
        result_data.append(d)

    # 存成.json檔案
    with open("test_kmeans.json", "w", encoding="utf-8") as f:
        json.dump(result_data, f, ensure_ascii=False, indent=4)

# 調用 K-means 函數
k_means(2, df_combined_scaled)

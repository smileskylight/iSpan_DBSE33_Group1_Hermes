import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from gensim.models import Word2Vec
from sklearn.metrics import pairwise_distances

# 读取原始数据
def get_rawdata(folder_path):
    result_list = []
    rawdata_file_names = [f for f in os.listdir(folder_path) if f.endswith(".json")]
    for file_name in rawdata_file_names:
        with open(os.path.join(folder_path, file_name), "r", encoding="utf-8") as file:
            data = json.load(file)
            result_list.extend(data)
    return result_list

folder_path = "./test2"
documents = get_rawdata(folder_path)
df = pd.DataFrame(documents)

# 预处理数据
stopword_file_path = './stopwords.txt'
stop_words = [line.strip() for line in open(stopword_file_path, 'r', encoding='utf-8')]

tag_documents = [document["tag"].split(",") for document in documents if "tag" in document and document["tag"]]
tag_model = Word2Vec(tag_documents, vector_size=100, window=2, sg=0, min_count=1, seed=42, epochs=20)

df['景點名稱_label'] = LabelEncoder().fit_transform(df['景點名稱'])
vectors_df = pd.DataFrame(tag_model.wv.vectors)
df_combined = pd.concat([df['景點名稱_label'], vectors_df], axis=1)
df_combined.columns = df_combined.columns.astype(str)

imputer = SimpleImputer(strategy='mean')
df_combined_filled = imputer.fit_transform(df_combined)
scaler_combined = StandardScaler()
df_combined_scaled = scaler_combined.fit_transform(df_combined_filled)

# 执行 K-means 聚类
kmeans = KMeans(n_clusters=12, random_state=42)
clusters = kmeans.fit_predict(df_combined_scaled)

# 计算聚类中心之间的距离矩阵
cluster_centers = kmeans.cluster_centers_
distance_matrix = pairwise_distances(cluster_centers, metric='euclidean')

# 将距离转换为相似度（这里简单地使用距离的倒数作为相似度，您可以根据需要选择不同的转换方式）
similarity_matrix = 1 / (1 + distance_matrix)

# 绘制聚类中心之间的相似度热力图
plt.figure(figsize=(10,10))
sns.heatmap(similarity_matrix, annot=True, cmap='coolwarm', linewidths=.5)
plt.title('Heatmap of Cluster Center Similarity')
plt.show()
sns.clustermap(similarity_matrix, metric="correlation", standard_scale=1, figsize=(12, 13), cmap="vlag")
plt.title('Hierarchical Clustered Scaled Heatmap with Seaborn')
plt.savefig('hierarchical_clustered_scaled_heatmap_with_Seaborn_clustermap.png', dpi=150)
plt.show()

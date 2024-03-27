import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_samples, silhouette_score
from sklearn.preprocessing import StandardScaler
import json
import os
from gensim.models import Doc2Vec, Word2Vec
from gensim.models.doc2vec import TaggedDocument
import jieba
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer
from yellowbrick.cluster import SilhouetteVisualizer
from sklearn.decomposition import PCA

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
# comment_model = Doc2Vec(vector_size=100, window=5, min_count=1, epochs=20)
# comment_model.build_vocab(comment_documents)
# comment_model.train(comment_documents, total_examples=comment_model.corpus_count, epochs=comment_model.epochs)
# comment_vectors = [comment_model.dv[i] for i in range(len(comment_documents))]

# 訓練 Word2Vec 模型
tag_model = Word2Vec(
    tag_documents, 
    vector_size=100,  
    window=2, 
    sg=1, 
    min_count=1,
    seed=42,
    epochs=20)

# 调整Word2Vec模型中标签向量的权重
tag_vectors_weighted = pd.DataFrame(tag_model.wv.vectors * 0.3)  # 将标签向量乘以一个小于1的权重

# 合併評論向量和加权的标签向量
df_combined = pd.concat([df['景點名稱_label'].astype(str), 
                         tag_vectors_weighted], axis=1)

# Convert column names to strings
df_combined.columns = df_combined.columns.astype(str)

# 填充 NaN 值並標準化數據
imputer = SimpleImputer(strategy='mean')
scaler_combined = StandardScaler()
df_combined_filled = pd.DataFrame(imputer.fit_transform(df_combined), columns=df_combined.columns)
df_combined_scaled = scaler_combined.fit_transform(df_combined_filled)


pca = PCA(n_components=0.95, random_state=0)
df_combined_pca = pca.fit_transform(df_combined_scaled)
# ks = range(1,50)
# inertias = [] #innertias = distance

# for k in ks:
    
#     model = KMeans(n_clusters=k)
#     model.fit(df_combined_pca)
#     inertias.append(model.inertia_)

# plt.figure(figsize=(10,6))
# plt.style.use("bmh")
# plt.plot(ks, inertias,"-o")
# plt.xlabel("K value")
# plt.ylabel("Inertias")
# plt.xticks(ks)
# plt.show()
# Change the start of the range from 0 to 2 (as 1 cluster does not make much sense for silhouette analysis)
for k in range(2,5):
    fig, ax = plt.subplots(1,1)
    fig.set_size_inches(18,7)
    
    km = KMeans(n_clusters=k, random_state=0)
    labels = km.fit_predict(df_combined_pca)

    silhouette_values = silhouette_samples(df_combined_pca, labels)
    y_lower, y_upper = 0, 0
    
    for index, cluster in enumerate(np.unique(labels)):
        cluster_silhouette_values = silhouette_values[labels == cluster]
        cluster_silhouette_values.sort()
         
        y_upper += len(cluster_silhouette_values)
        
        ax.barh(range(y_lower, y_upper), cluster_silhouette_values, height=1)
        ax.text(-0.05,(y_lower + y_upper) / 2, str(cluster))
        
        y_lower += len(cluster_silhouette_values)

        avg_score = np.mean(silhouette_values)
        ax.axvline(avg_score, linestyle="--", linewidth=2, color="green")
        ax.set_yticks([])
    
        ax.set_xlabel("Silhouette Coefficient Values")
        ax.set_ylabel("Cluster Labels")
        ax.set_title(f"Silhouette plot for the various clusters with k={k}")


for i, k in enumerate(range(2,5)):
    model = KMeans(n_clusters=k, random_state=0)
    visualizer = SilhouetteVisualizer(model, colors="yellowbrick")
    
    visualizer.fit(df_combined_pca)
    visualizer.show()

# from sklearn.decomposition import PCA

# pca = PCA(random_state=0)
# pca.fit(df_combined_scaled)

# components = range(pca.n_components_)
# # components


# variance = pca.explained_variance_
# # pca.explained_variance_
# plt.figure(figsize=(8,4))
# plt.bar(components[:10], variance[:10], color="lightskyblue")
# plt.xlabel("PCA Components")
# plt.ylabel("Variance")
# plt.xticks(components[:10])
# plt.show()


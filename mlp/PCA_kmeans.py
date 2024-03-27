from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, silhouette_samples
import matplotlib.pyplot as plt
import numpy as np
from gensim.models import Doc2Vec, Word2Vec
from gensim.models.doc2vec import TaggedDocument
import jieba
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer
import json
import os


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
    if specific_tag_key in document and document[specific_tag_key] != '':
        tags = document[specific_tag_key].split(",")
        filtered_tags = [tag.strip() for tag in tags if tag.strip() not in stop_words]
        tag_documents.append(filtered_tags)
    else:
        tag_documents.append([])

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
# 定义用于读取原始数据和预处理的函数...

# 训练 Doc2Vec 和 Word2Vec 模型，生成特征向量...

# 合并评论向量和标签向量，填充NaN值，标准化数据...
# 假设最终用于聚类的数据存储在 df_combined_scaled 中

# 定义测试的k值范围
k_range = range(2,50)
silhouette_coefficients = []

# 对每个k值进行K-means聚类和轮廓系数计算
for k in k_range:
    kmeans = KMeans(n_clusters=k, random_state=42).fit(df_combined_scaled)
    score = silhouette_score(df_combined_scaled, kmeans.labels_)
    silhouette_coefficients.append(score)

# 找出轮廓系数最大的k值
max_score = max(silhouette_coefficients)
optimal_k = k_range[silhouette_coefficients.index(max_score)]

print(f'輪廓係數最大时的k值為：{optimal_k}')

# 可选：绘制k值与轮廓系数的关系图
plt.plot(k_range, silhouette_coefficients)
plt.xticks(k_range)
plt.xlabel('k')
plt.ylabel('silhouette_score')
plt.title('k and silhouette_score')
plt.show()

# 使用最佳k值进行K-means聚类
kmeans = KMeans(n_clusters=optimal_k, random_state=42)
df['cluster'] = kmeans.fit_predict(df_combined_scaled)

# 继续后续分析...
from sklearn.decomposition import PCA

# 假设 df_combined_scaled 是经过预处理和特征提取的数据集
# 使用最佳k值进行K-means聚类
kmeans = KMeans(n_clusters=optimal_k, random_state=42)
clusters = kmeans.fit_predict(df_combined_scaled)

# 使用PCA将数据降维到2维，以便可视化
pca = PCA(n_components=2)
df_pca = pca.fit_transform(df_combined_scaled)

# 绘制聚类结果的散点图
plt.figure(figsize=(10, 8))
plt.scatter(df_pca[:, 0], df_pca[:, 1], c=clusters, cmap='viridis', marker='o', edgecolor='k', s=50)
plt.xlabel('PCA 1')
plt.ylabel('PCA 2')
plt.title('Cluster Visualization with PCA')
plt.colorbar()
plt.show()



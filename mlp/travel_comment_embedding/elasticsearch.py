# import packages
import requests
import json
import re
from travel_comment_embedding.vector import TextEmbedder
from dotenv import load_dotenv
import os


# # Load environment variables from .env file
# load_dotenv()

# # Accessing variables
# BASE_URL = os.getenv("BASE_URL")
# username = os.getenv("ES_USERNAME")
# password = os.getenv("PASSWORD")


# comment vector
def get_comments_from_txt(file_path):

    result_all = []
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            result_all.append(eval(line))

    return result_all


# attraction name
def get_point_from_txt(file_path):

    result_point = []
    with open(file_path, "r", encoding="utf-8-sig") as file:
        for line in file:
            line = line.split(" ")[0]
            result_point.append(line)

    return result_point


def setup_elasticsearch_index(base_url, username, password):
    """
    Creates an Elasticsearch index for storing comments with their vector representations.
    """
    url = f"{base_url}_cat/indices"
    auth = (username, password)
    headers = {"Content-Type": "application/json"}
    data = {
        "mappings": {
            "properties": {
                "comment_vector": {
                    "type": "dense_vector",
                    "dims": 312,
                    "index": True,
                    "similarity": "cosine",
                },
                "tag": {"type": "keyword"},
            }
        }
    }
    response = requests.put(
        f"{base_url}vec_comment_retry",
        auth=auth,
        headers=headers,
        data=json.dumps(data),
    )
    print(response.json())


def bulk_import_comments(base_url, username, password, result_all, result_point):
    """
    Imports comments into Elasticsearch in chunks.
    """

    def es_bulk_import(slice_start, slice_end, file):
        headers = {"Content-Type": "application/x-ndjson"}
        bulk_data = ""
        global_id = slice_start + 1  # Ensure unique IDs across slices

        # Adjust for the last slice which may not be exactly 10,000 in size
        slice_end = min(slice_end, len(result_all))

        for idx in range(slice_start, slice_end):
            bulk_data += json.dumps({"index": {"_id": f"{global_id}"}}) + "\n"
            bulk_data += (
                json.dumps(
                    {"comment_vector": result_all[idx], "tag": f"{result_point[idx]}"}
                )
                + "\n"
            )
            global_id += 1

        response = requests.post(
            f"{base_url}vec_comment_retry/_bulk",
            auth=(username, password),
            headers=headers,
            data=bulk_data,
        )
        file.write(
            f"Imported slice {slice_start} to {slice_end}, Response: {response.json()}\n"
        )

    # 準備寫入進度到檔案
    with open("import_progress.txt", "w") as file:
        # Loop through the dataset in chunks
        for i in range(0, len(result_all), 10000):
            es_bulk_import(
                i, min(i + 10000, len(result_all)), file
            )  # 確保最後一批處理正確


def match_query(base_url, username, password, query_vec):
    """
    Executes a k-NN query to find similar comments based on a query vector.
    """
    headers = {"Content-Type": "application/json"}
    query_data = {
        "knn": {
            "field": "comment_vector",
            "query_vector": query_vec,
            "k": 30,
            "num_candidates": 1000,
        },
        "fields": ["comment_vector", "tag"],
    }
    result = requests.get(
        f"{base_url}vec_comment_retry/_knn_search",
        auth=(username, password),
        headers=headers,
        data=json.dumps(query_data),
    )
    # print(result.json())

    matches = result.json()["hits"]["hits"]
    result_list = [match["_source"]["tag"] for match in matches]
    result_list = list(set(result_list))

    return result_list


# # Example usage:
if __name__ == "__main__":
    #     # Load data
    #     result_all = get_comments_from_txt(
    #         "./travel_comment_embedding/data/travel_comment_vec_test.txt"
    #     )
    #     result_point = get_point_from_txt(
    #         "./travel_comment_embedding/data/travel_comment_clean.txt"
    #     )

    #     # Set up Elasticsearch index
    #     setup_elasticsearch_index(
    #         "http://localhost:9200/", "elastic", "My=j_Grks0N5A8w7Eh9u"
    #     )

    #     # Bulk import comments into Elasticsearch
    #     bulk_import_comments(
    #         "http://localhost:9200/",
    #         "elastic",
    #         "My=j_Grks0N5A8w7Eh9u",
    #         result_all,
    #         result_point,
    #     )

    # Example query
    query_text = "寧靜、探索、山間之旅"
    embedder = TextEmbedder()
    query_vec = embedder.texts_to_embeddings([query_text])[0].tolist()[
        0
    ]  # Assuming this method returns a list of embeddings

    # Execute query
    matches = match_query(
        "http://192.168.1.205:9200/", "elastic", "My=j_Grks0N5A8w7Eh9u", query_vec
    )
    # print(matches)

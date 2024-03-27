# -*- coding: utf-8 -*-
import requests as rq
from bs4 import BeautifulSoup as bs
from fake_useragent import UserAgent
from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_cors import CORS
from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pymongo import MongoClient

app = Flask(__name__, static_folder="static")
CORS(app)

mongo_uri = "mongodb+srv://root:Anny12345!@cluster0.sbvqogz.mongodb.net/Taiwan_travel"
client = MongoClient(mongo_uri)
db = client["Taiwan_travel"]
collection = db["data"]

# llm = ChatOpenAI(openai_api_key="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")


@app.route("/api/submit", methods=["POST"])
def submit():
    if not request.json or "user_input" not in request.json:
        return jsonify({"error": "缺少用户输入"}), 400

    user_input = request.json["user_input"]

    # 调用处理函数
    ai_response = process_input(user_input)

    return jsonify({"ai_response": ai_response})


def process_input(user_input):
    prompt = f"""
    你是一個旅遊機器人，請根據用戶輸入的問題，擷取出和問題相關的重要關鍵字。
    用戶問題：
    {user_input}
    關鍵字：
    """
    messages = [SystemMessage(content=prompt), HumanMessage(content=user_input)]
    output = llm.invoke(messages)
    print(type(output.content))
    return output.content


def get_images_def(image_urls):
    urls = image_urls
    link_hrefs = []
    for url in urls:
        ua = UserAgent()
        my_header = {"user-agent": ua.random}

        ans = rq.get(url, headers=my_header)
        root = bs(ans.text, "lxml")

        link_href = root.find("meta", property="og:image")["content"]
        link_hrefs.append(link_href)

    return link_hrefs


place_names = [
    "蚵仔寮海邊沙灘",
    "夏都沙灘酒店海灘",
    "八里北堤沙灘",
    "竹圍海水浴場",
]


@app.route("/")
def show_places():
    places_info = []
    for place_name in place_names:
        place_data = collection.find_one(
            {"景點名稱": place_name},
            {
                "_id": 0,
                "Google評論網址": 1,
                "景點名稱": 1,
                "地址": 1,
                "緯度": 1,
                "經度": 1,
            },
        )
        if place_data:
            picture_hrefs = (
                get_images_def([place_data["Google評論網址"]])
                if "Google評論網址" in place_data
                else []
            )
            places_info.append(
                {
                    "name": place_data["景點名稱"],
                    "address": place_data.get("地址", "Address not available"),
                    "pictures": picture_hrefs,
                    "latitude": place_data.get("緯度"),
                    "longitude": place_data.get("經度"),
                }
            )
        else:
            # 处理查询不到的情况
            print(f"找不到地點: {place_name}")
    return render_template("recommend_damo.html", places=places_info)


if __name__ == "__main__":
    app.run(debug=True, port=5502)

import asyncio
import json
import os
import random
import re
import sys
import threading
import typing as t

import requests as rq
from bs4 import BeautifulSoup as bs
from dotenv import find_dotenv, load_dotenv
from fake_useragent import UserAgent
from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from flask_cors import CORS
from joblib import Parallel, delayed
from langchain.schema import HumanMessage, SystemMessage
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_openai import ChatOpenAI
from pymongo import MongoClient
from travel_comment_embedding.elasticsearch import match_query
from travel_comment_embedding.vector import TextEmbedder

sys.path.append("")

app = Flask(__name__, static_folder="static")
CORS(app)

mongo_uri = "mongodb+srv://root:Anny12345!@cluster0.sbvqogz.mongodb.net/Taiwan_travel"
client = MongoClient(mongo_uri)
db = client["Taiwan_travel"]
collection = db["data"]
load_dotenv(find_dotenv(), override=True)
llm = ChatOpenAI()
app.secret_key = os.getenv("FLASK_SECRET_KEY")


def get_matches(user_input):
    # Step 1: 提取关键词
    keywords = extract_keywords(user_input)
    # Step 2: 使用Elasticsearch进行查询
    matches = search_with_elasticsearch(keywords)
    return matches


def get_final_response(matches):
    # Step 3: 使用DuckDuckGo进行搜索，获取更多信息
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    search_results = duckduckgo_search_threaded(matches)
    print(search_results)

    # Step 4: 摘要旅游评论，提炼出重要信息
    summaries = summarize_travel_comments(search_results)
    print(summaries)

    # Step 5: 生成最终的旅游行程规划
    start_response()
    final_itinerary = generate_final_output(summaries)
    print(final_itinerary)
    end_response()

    # 将最终行程规划整合成一个字符串，以便以JSON格式返回

    final_response = [itinerary for itinerary in final_itinerary]

    return final_response


@app.route("/")
def index():
    session.clear()  # 清理session
    return render_template("index.html")


@app.route("/api/submit", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        if not request.json or "user_input" not in request.json:
            return jsonify({"error": "缺少用户输入"}), 400
        user_input = request.json["user_input"]

        session["matches"] = get_matches(user_input)

        session["final_response"] = get_final_response(session["matches"])

        return jsonify({"message": session["final_response"]})
        # 返回最终的旅游行程规划

    elif request.method == "GET":
        # 检查session中是否存储了之前的响应结果
        final_response = session.get(
            "final_response", {"message": "没有找到最终的旅游行程规划"}
        )
        return jsonify(final_response)


def start_response():
    # 这个函数可能需要调整为返回一个字符串，而不是直接打印
    return "我为您精选了一些不可错过的景点与活动。以下是关于您感兴趣的目的地的一些精彩介绍，以及我个人推荐的行程安排：\n"


def end_response():
    # 同上，调整为返回一个字符串
    return "希望以上的信息能够帮助您规划一次难忘的旅行。"


def extract_keywords(user_input):
    llm = ChatOpenAI()
    prompt = f"""
    你是一個旅遊機器人，請根據用戶輸入的問題，擷取出和問題相關的重要關鍵字。
    用戶問題： ```{user_input}```
    關鍵字：
    """
    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=user_input),  # user input
    ]
    output = llm.invoke(messages)
    pattern = r"^關鍵字："
    output_user_sum = re.sub(pattern, "", output.content)
    # print(output_user_sum.strip())
    # print(type(output_user_sum.strip()))
    return output_user_sum.strip()


def search_with_elasticsearch(query_text):
    embedder = TextEmbedder()
    query_vec = embedder.texts_to_embeddings([query_text])[0].tolist()[0]
    matches = match_query("http://104.43.104.71:9200/", "elastic", "aa0990", query_vec)
    return random.sample(matches, 4)


def duckduckgo_search_threaded(random_matches_es):
    api_wrapper = DuckDuckGoSearchAPIWrapper(
        max_results=3, safesearch="moderate", time="m"
    )
    search = DuckDuckGoSearchResults(
        api_wrapper=api_wrapper, source="web"
    )  # web news images videos blogs forums
    search_list = []

    for attr in random_matches_es:
        output = search.run(attr)
        pattern = r"snippet: (.*?), title: (.*?), link: (.*?)\],"
        matches = re.findall(pattern, output, re.DOTALL)
        for snippet, title, link in matches:
            search_list.append(f"Title: {title}\nSnippet: {snippet}\nLink: {link}\n\n")
    return ["".join(search_list[i : i + 3]) for i in range(0, len(search_list), 3)]


def summarize_travel_comments(grouped_lst):
    llm = ChatOpenAI()
    summary = []
    for comment in grouped_lst:
        prompt = f"""
        你是一個旅遊行程規劃專家，請根據以上旅遊相關文本，擷取出重要內容，並全部以繁體中文回應：
        文本內容: ```{comment}```
        旅遊摘要:
        """
        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=comment),  # user input
        ]
        output = llm.invoke(messages)
        summary.append(output.content.strip())
    return summary


def generate_final_output(summary):
    llm = ChatOpenAI(model_name="gpt-4-turbo-preview")
    final_summary = []
    for sum in summary:

        sys = f"""
        你現在是一個旅遊行程規劃專家，請根據文本摘要內容，規劃出行程，依照以下格式，用繁體中文產生旅遊回應:

        格式:

        [景點名稱] - [地點]
        景點介紹: 
        [詳細介紹該景點的歷史背景、特色，提供景點的基本資訊，以及周邊推薦的住宿、餐廳]
        推薦活動/行程安排：
        [活動/行程1] - [詳細介紹活動內容、所需時間、是否需要預約等資訊。]
        [活動/行程2] - [同上]
        [活動/行程3] - [同上]
        """
        query = f"""
        摘要內容: ```{sum}```
        """
        messages = [
            SystemMessage(content=sys),
            HumanMessage(content=query),  # Summarized content
        ]
        output = llm.invoke(messages)
        final_summary.append(output.content.strip())
    return final_summary


def start_response():
    print(
        f"我為您精選了一些不可錯過的景點與活動。以下是關於您感興趣的目的地的一些精彩介紹，以及我個人推薦的行程安排：\n"
    )


def end_response():
    print("希望以上的資訊能夠幫助您規劃一次難忘的旅行。")


def get_images_def(image_urls):
    urls = image_urls
    link_hrefs = []
    for url in urls:
        ua = UserAgent()
        my_header = {"user-agent": ua.random}

        try:
            ans = rq.get(url, headers=my_header)
            root = bs(ans.text, "lxml")

            meta_tag = root.find("meta", property="og:image")
            if meta_tag and "content" in meta_tag.attrs:
                link_href = meta_tag["content"]
                link_hrefs.append(link_href)
            else:
                # 如果没有找到图片，可以追加一个默认图片链接或者留空
                print("No image found for URL:", url)
                # link_hrefs.append("default_image_url") # 例子：添加默认图片链接
        except Exception as e:
            print("Error fetching URL:", url, "Error:", e)
            # 在出现错误时，可以选择追加默认图片链接或者留空
            # link_hrefs.append("default_image_url") # 例子：添加默认图片链接

    return link_hrefs


@app.route("/places4", methods=["GET"])
def show_places():
    places_info = []
    place_names = session.get("matches", [])
    print(place_names)
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
    return render_template("recommend.html", places=places_info)


if __name__ == "__main__":
    app.run(debug=True, port=5502)

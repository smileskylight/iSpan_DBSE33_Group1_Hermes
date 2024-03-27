import random
import re
import sys

from dotenv import find_dotenv, load_dotenv
from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

sys.path.append("")
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper

from travel_comment_embedding.elasticsearch import match_query
from travel_comment_embedding.vector import TextEmbedder

# Authenticate to OpenAI
load_dotenv(find_dotenv(), override=True)


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
    matches = match_query(
        "http://localhost:9200/", "elastic", "My=j_Grks0N5A8w7Eh9u", query_vec
    )
    return random.sample(matches, 5)


def duckduckgo_search(random_matches_es):
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


# Example usage:
user_input = "我想踏上一次寧靜而充滿探索的山間之旅"
keywords = extract_keywords(user_input)
matches = search_with_elasticsearch(keywords)
search_results = duckduckgo_search(matches)
summaries = summarize_travel_comments(search_results)
final_itinerary = generate_final_output(summaries)

start_response()
for itinerary in final_itinerary:
    print(itinerary)
    print("-" * 100)
end_response()

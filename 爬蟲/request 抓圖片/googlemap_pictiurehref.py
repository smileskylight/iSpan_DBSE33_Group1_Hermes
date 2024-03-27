import json
import os

# 假設這是一個示例，實際上不應該在這個環境中運行 requests 和 BeautifulSoup
import requests as rq
from bs4 import BeautifulSoup as bs
from fake_useragent import UserAgent


def get_images_def(image_urls):
    # 從JSON數據中提取景點名稱和評論網址
    urls = image_urls
    link_hrefs = []
    for url in urls:  # 遍歷所有URL
        ua = UserAgent()
        my_header = {"user-agent": ua.random}

        ans = rq.get(url, headers=my_header)
        root = bs(ans.text, "lxml")

        #  抓網址
        link_href = root.find("meta", property="og:image")["content"]

        # 將抓取的鏈接添加到列表中
        link_hrefs.append(link_href)

    return link_hrefs

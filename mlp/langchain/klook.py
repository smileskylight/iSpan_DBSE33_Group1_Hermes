from time import sleep
from urllib.parse import parse_qs, urlparse

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from IPython.display import clear_output
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def initialize_browser():
    ua = UserAgent()
    user_agent = ua.random

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--incognito")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-notifications")
    options.add_argument("--lang=zh-TW")
    options.add_argument("--headless")
    options.add_argument(f"--user-agent={user_agent}")

    driver = webdriver.Chrome(options=options)

    return driver


def google_search(keyword):
    keyword = f"{keyword} site:www.klook.com"
    driver = initialize_browser()
    driver.get("https://www.google.com/")

    search_element = driver.find_element(By.NAME, "q")
    search_element.send_keys(keyword)
    search_element.send_keys(Keys.ENTER)
    sleep(2)
    url_resl = driver.find_elements(By.CSS_SELECTOR, ".g .yuRUbf a")
    url_list = [link.get_attribute("href") for link in url_resl]
    if len(url_list) > 5:
        url_list = url_list[:5]

    return url_list


def get_data(url):
    """从网址中获取地址"""
    ua = UserAgent()
    my_header = {
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, zstd",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "max-age=0",
        "Referer": "https://www.kkday.com/zh-tw",
        "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
    }
    my_cookies = {
        "csrf_cookie_name": "eb4ca2dfb7da8c052155126eda496820",
        "KKWEB": "a%3A4%3A%7Bs%3A10%3A%22session_id%22%3Bs%3A32%3A%22e0cea8e1bf5723d07a8fba309451ec6b%22%3Bs%3A7%3A%22channel%22%3Bs%3A5%3A%22GUEST%22%3Bs%3A13%3A%22last_activity%22%3Bi%3A1709534864%3Bs%3A9%3A%22user_data%22%3Bs%3A0%3A%22%22%3B%7D63c890565df9e4a6b6b3a1f06315b47a",
        "country_lang": "zh-tw",
        "currency": "TWD",
        "KKUD": "e0cea8e1bf5723d07a8fba309451ec6b",
        "_gcl_au": "1.1.1678763949.1709534863",
        "__lt__cid": "4a8f4139-f8e4-4fc8-8c66-486b8ee2c5c1",
        "__lt__sid": "dc5190f0-cb1b6932",
        "_gid": "GA1.2.1916222337.1709534865",
        "_fbp": "fb.1.1709534865054.1182344073",
        "_hjSession_628088": "eyJpZCI6ImFmOGU4ZmIzLTI1OGUtNGQ3ZC04MThjLTA2MDBiMDAyMmJhNiIsImMiOjE3MDk1MzQ4NjUxMjgsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjoxLCJzcCI6MH0=",
        "rskxRunCookie": "0",
        "rCookie": "32s4yeoj43953f3hgtwhpxltckx500",
        "_hjSessionUser_628088": "eyJpZCI6ImIwYTZlZDJiLWM3MTctNThiNi04NmIxLTdjZGMzOTZkNTZhNyIsImNyZWF0ZWQiOjE3MDk1MzQ4NjUxMjcsImV4aXN0aW5nIjp0cnVlfQ==",
        "_ga_RJJY5WQFKP": "GS1.1.1709534864.1.1.1709534999.58.0.0",
        "_ga": "GA1.2.1165163055.1709534865",
        "_dc_gtm_UA-49763723-1": "1",
        "_dc_gtm_UA-117438867-1": "1",
        "datadome": "gGdOkSBQ7stTxVwxNtV0l7is1MPCQB~yZh18w2qO5qlueVhBi2G_xe9rdu3HVV~19CGV9MECCQSWORsF19fhylzBdSz6jHlcPJuRnTJmtCrFuSaqNryT41glZ8MCCfaU",
        "lastRskxRun": "1709534999904",
        "_uetsid": "1b79a100d9f311eebc16f7a9f4eda697",
        "_uetvid": "1b79a0b0d9f311eea915efe0950cd462",
        "cto_bundle": "MjiTbF9ySlFEeEt5ZmltY004biUyRkh5TENScEI1SE9VdmIlMkJYMXlHQ3VlamVReEpBaTdXYXJkWTZSWFZEall0b3NxVm9adUJ4aTFWRWxPT0lqQU9WWm1abWRZVER2RmxVSjV4YlpKeUFMbkxXRVBGWmx0SHB2MnFkeW00OEowNXZBamZ3c2Q2MVVwVEd2OENMRkc5S3RCNTJNMUNBJTNEJTNE",
    }

    response = requests.get(url, headers=my_header, cookies=my_cookies)

    soup = BeautifulSoup(response.text, "html5lib")
    print(response.encoding)
    datas = [
        data.get_text()
        for data in soup.find_all(["title", "h1", "h2", "h3", "p", "div"])
    ]

    return datas


def get_klook_data(keyword):
    keyword_google_search = f"{keyword}  site:www.klook.com"
    return_list = [get_data(url) for url in google_search(keyword_google_search)]

    return return_list

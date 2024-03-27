'''
匯入套件
'''
# 操作 browser 的 API
from selenium.webdriver.chrome.service import Service
from selenium import webdriver

# 處理逾時例外的工具
from selenium.common.exceptions import TimeoutException

# 面對動態網頁，等待某個元素出現的工具，通常與 exptected_conditions 搭配
from selenium.webdriver.support.ui import WebDriverWait

# 搭配 WebDriverWait 使用，對元素狀態的一種期待條件，若條件發生，則等待結束，往下一行執行
from selenium.webdriver.support import expected_conditions as EC

# 期待元素出現要透過什麼方式指定，通常與 EC、WebDriverWait 一起使用
from selenium.webdriver.common.by import By

# 強制等待 (執行期間休息一下)
from time import sleep

# send_keys模擬鍵盤輸入
from selenium.webdriver.common.keys import Keys

# ChromeDriver 的下載管理工具
from webdriver_manager.chrome import ChromeDriverManager

# 下載檔案的工具
import wget

# 文字修飾
from pprint import pprint,pformat

from bs4 import BeautifulSoup

import pandas as pd

'''
selenium 啓動 Chrome 的進階配置參數
參考網址：https://stackoverflow.max-everyday.com/2019/12/selenium-chrome-options/
'''
# 啟動瀏覽器工具的選項
my_options = webdriver.ChromeOptions()
# my_options.add_argument("--headless")                #不開啟實體瀏覽器背景執行
my_options.add_argument("--start-maximized")           #最大化視窗
my_options.add_argument("--incognito")                 #開啟無痕模式
my_options.add_argument("--disable-popup-blocking")    #禁用彈出攔截
my_options.add_argument("--disable-notifications")     #取消 chrome 推播通知
my_options.add_argument("--lang=zh-TW")                #設定為正體中文


# 使用 Chrome 的 WebDriver
# my_service = Service(executable_path="./chromedriver.exe")
driver = webdriver.Chrome(
    options = my_options,
#     service = my_service
)
# 從文本文件中讀取景點名稱
titles = []
articles_data = []
needtoread = input('你要放入的檔案名稱 (Ex.一二三.txt,請輸入一二三,請放在同個目錄下): ')
with open(f'{needtoread}.txt', 'r', encoding='utf-8') as file:
    title_read = eval(file.read())
    # 印出每一個景點名稱
    for sublist in title_read:
        title_pattern = sublist[0]
        titles.append(title_pattern)
print(titles)

# 遍歷所有景點名稱，爬取維基百科上的信息
for title in titles:
    url = f'https://zh.wikipedia.org/zh-tw/{title}'
    driver.get(url)

    # 使用WebDriverWait等待頁面元素加載
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'firstHeading'))
        )
    except TimeoutException:
        print(f"頁面 {title} 加載超時")
        continue

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    title = soup.find('h1', id='firstHeading')
    content = soup.find('div', class_='mw-parser-output')

    if content and title:
        article_info = {
            'title': title.get_text().strip(),
            'content': ' '.join([p.get_text() for p in content.find_all('p') if p.get_text().strip() != ''])
        }
        articles_data.append(article_info)
    else:
        print(f"頁面 {title} 是空白頁面或不包含預期內容")

# 關閉瀏覽器
driver.quit()

# 將文章數據轉換成DataFrame，並保存到CSV文件
df = pd.DataFrame(articles_data)
df.to_csv('wikipedia_data.csv', index=False, encoding='utf-8-sig')
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import pandas as pd

# 讀取JSON文件
with open('桃園市桃園區.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# 從JSON數據中提取景點名稱
wiki_pages = [item["景點名稱"] for item in data]

# 配置Chrome選項以運行無頭模式
chrome_options = Options()
chrome_options.add_argument("--headless")

# 使用 webdriver-manager 自動管理 ChromeDriver
service = Service(ChromeDriverManager().install())
browser = webdriver.Chrome(service=service, options=chrome_options)

articles_data = []

# 遍歷所有景點名稱，爬取維基百科上的信息
for page_title in wiki_pages:
    url = f'https://zh.wikipedia.org/zh-tw/{page_title}'
    browser.get(url)

    # 使用WebDriverWait等待頁面元素加載
    try:
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, 'firstHeading'))
        )
    except TimeoutException:
        print(f"頁面 {page_title} 加載超時")
        continue

    soup = BeautifulSoup(browser.page_source, 'html.parser')
    title = soup.find('h1', id='firstHeading')
    content = soup.find('div', class_='mw-parser-output')

    if content and title:
        article_info = {
            'title': title.get_text().strip(),
            'content': ' '.join([p.get_text() for p in content.find_all('p') if p.get_text().strip() != ''])
        }
        articles_data.append(article_info)
    else:
        print(f"頁面 {page_title} 是空白頁面或不包含預期內容")

# 關閉瀏覽器
browser.quit()

# 將文章數據轉換成DataFrame，並保存到CSV文件
df = pd.DataFrame(articles_data)
df.to_csv('wikipedia_data5.csv', index=False, encoding='utf-8-sig')

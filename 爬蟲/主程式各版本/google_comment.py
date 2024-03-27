import json
import os
from pprint import pformat, pprint
from time import sleep

import wget
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

my_options = webdriver.ChromeOptions()
# my_options.add_argument("--headless")                #不開啟實體瀏覽器背景執行
my_options.add_argument("--start-maximized")
my_options.add_argument("--incognito")
my_options.add_argument("--disable-popup-blocking")
my_options.add_argument("--disable-notifications")
my_options.add_argument("--lang=zh-TW")


driver = webdriver.Chrome(
    options=my_options,
)


# 你存放之前爬下來資料的資料夾位置
wheredata = "./your_folder"
# 你放要放評論的資料夾位置
put_comment_data = "./output_folder"
path = r"{}".format(wheredata)

files = os.listdir(path)
try:
    the_city = put_comment_data + "/done_folder"
    put_comment_data_file_names = [
        f for f in os.listdir(the_city) if f.endswith(".txt")
    ]
    put_comment_data_file_names_str = " ".join(put_comment_data_file_names)
except Exception as e:
    print(f"Error: {e}")

for file in files:

    position = os.path.join(path, file)

    title = os.path.basename(position)
    title_name = os.path.splitext(title)[0]

    with open(position, "r", encoding="utf-8") as file:

        data = json.load(file)

        for item in data:
            href = item["Google評論網址"]
            name = item["景點名稱"]
            # 檢查是否爬過
            if name in put_comment_data_file_names_str:
                continue
            driver.get(href)
            sleep(1)
            try:
                btn = driver.find_element(
                    By.XPATH,
                    '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[3]/div/div/button[2]',
                )
                btn.click()

            except Exception as e:
                print(f"Error: {e}")
                continue

            innerHeight = 0
            offset = 0
            count = 0
            limit = 5

            commentstars_ = []
            comments_ = []

            while count <= limit:

                commentstars_.clear()
                comments_.clear()

                try:
                    target_div = driver.find_element(
                        By.XPATH,
                        '//*[@class="m6QErb DxyBCb kA9KIf dS8AEf " and @tabindex="-1"]',
                    )
                    offset = driver.execute_script(
                        "return arguments[0].scrollHeight;", target_div
                    )
                    try:
                        target_element = WebDriverWait(driver, 10).until(
                            EC.visibility_of_element_located(
                                (
                                    By.XPATH,
                                    '//*[@class="m6QErb DxyBCb kA9KIf dS8AEf " and @tabindex="-1"]',
                                )
                            )
                        )

                        driver.execute_script(
                            "arguments[0].scrollTo({ top: arguments[0].scrollTop + 2500, behavior: 'smooth' });",
                            target_element,
                        )
                        sleep(1)
                        btn2s = driver.find_elements(
                            By.XPATH,
                            '//*[@class="w8nwRe kyuRq" and @aria-expanded="false"]',
                        )
                        for btn2 in btn2s:
                            btn2.click()
                            sleep(0.01)

                    except Exception as e:
                        print(f"Error: {e}")

                    innerHeight = driver.execute_script(
                        "return arguments[0].scrollHeight;", target_div
                    )
                except Exception as e:
                    print(f"Error: {e}")
                if offset == innerHeight:
                    count += 1
                elif offset != innerHeight:
                    count = 0

            commentstars = driver.find_elements(
                By.XPATH, '//*[@class="kvMYJc" and @role="img"]'
            )
            for commentstar in commentstars:
                aria_label = commentstar.get_attribute("aria-label")
                commentstars_.append(aria_label)

            comments = driver.find_elements(By.CSS_SELECTOR, "span.wiI7pd")
            for comment in comments:
                comments_.append(comment.text)

            combined_data = list(zip(commentstars_, comments_))

            merged_data = []

            for data in combined_data:
                merged_data.append(f"{data[0]} {data[1]}")

            new_path = rf"{put_comment_data}\{title_name}"
            if not os.path.isdir(new_path):
                os.mkdir(new_path)

            with open(f"{new_path}\{name}.txt", "w", encoding="utf-8") as file:
                file.write(str(merged_data))
driver.close()

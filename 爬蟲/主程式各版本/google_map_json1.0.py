from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import pandas as pd
import json
import csv
import re

from urllib.parse import urlparse, parse_qs


def initialize_browser():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--incognito")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-notifications")
    options.add_argument("--lang=zh-TW")

    driver = webdriver.Chrome(options=options)
    print("scraping start...")
    return driver

def navigate_to_google_maps(driver, query):# 搜尋
    try:
        driver.get("https://www.google.com/maps/")
        search_element = driver.find_element(By.CSS_SELECTOR, "input#searchboxinput.searchboxinput.xiQnY")
        search_element.send_keys(query)
        search_element.send_keys(Keys.ENTER)
        sleep(3)
        search_element.send_keys(Keys.BACKSPACE, Keys.BACKSPACE, Keys.BACKSPACE, Keys.BACKSPACE, Keys.BACKSPACE, Keys.BACKSPACE, Keys.BACKSPACE, Keys.BACKSPACE, Keys.BACKSPACE, Keys.BACKSPACE)
        search_element.send_keys("旅遊景點")
        search_element.send_keys(Keys.ENTER)
        sleep(1)
    except Exception as e:
        print(f"navigate_to_google_maps _ an error occurred: {e}")

# Example usage
# driver = webdriver.Chrome() # Or any other browser driver
# navigate_to_google_maps(driver, "Your Query")

def scroll_page(driver): #滾動
    try:
        target_element = driver.find_element(By.XPATH, '//*[@class="m6QErb DxyBCb kA9KIf dS8AEf ecceSd" and @role="feed"]')
        driver.execute_script("arguments[0].scrollTo({ top: arguments[0].scrollTop + 200, behavior: 'smooth' });",
                              target_element)
        sleep(0.5)
        innerHeight = 0
        offset = 0
        count = 0
        limit = 5
        # 可是內容調整n要滑幾次
        while count <= limit:
            
            target_div = driver.find_element(By.XPATH, '//*[@class="m6QErb DxyBCb kA9KIf dS8AEf ecceSd QjC7t" ]')
            offset = driver.execute_script('return arguments[0].scrollHeight;', target_div)
            # print(f'offset: {offset}')
            try:
                target_element = driver.find_element(By.XPATH, '//*[@class="m6QErb DxyBCb kA9KIf dS8AEf ecceSd QjC7t" ]')

                # 在垂直方向下滾動 2500 像素
                driver.execute_script("arguments[0].scrollTo({ top: arguments[0].scrollTop + 2500, behavior: 'smooth' });", target_element)
                sleep(1)
                
            except Exception as e:
                print(f"Error: {e}")

            innerHeight = driver.execute_script('return arguments[0].scrollHeight;', target_div)
            # print(f'innerHeight: {innerHeight}')
            # print(f'count: {count}')
            
            if offset == innerHeight:
                count += 1
            elif offset != innerHeight :
                count = 0
    except Exception as e:
        print(f"scroll_page _ An error occurred: {e}")

# Example usage
# driver = webdriver.Chrome() # Or any other browser driver
# scroll_page(driver)


def extract_attractions_info(driver):# 抓景點名 href 全部有幾星跟幾條評論 (第一層爬蟲)
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.qBF1Pd.fontHeadlineSmall')))
        titles = [element.text for element in driver.find_elements(By.CSS_SELECTOR, '.qBF1Pd.fontHeadlineSmall')]

        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.hfpxzc')))
        hrefs = [element.get_attribute("href") for element in driver.find_elements(By.CSS_SELECTOR, 'a.hfpxzc')]

        star_and_comments = []
        for elements in driver.find_elements(By.CSS_SELECTOR, 'span.e4rVHe.fontBodyMedium'):
            if elements.text == '沒有評論':
                star_and_comments.append(elements.text)
                continue
            child_spans = elements.find_element(By.XPATH, './/span')
            star_and_comments.append(child_spans.get_attribute("aria-label"))

        return list(zip(titles, hrefs, star_and_comments))
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

# Example usage
# driver = webdriver.Chrome() # Or any other browser driver
# info = extract_attractions_info(driver)


def extract_additional_info_stars_and_tags(driver, hrefs):
    areas = []
    times = []
    stars = []
    tag = []

    for href in hrefs:
        try:
            driver.get(href)
            sleep(0.5)

            #景點的地點(第二層爬蟲)
            try:
                area_element = driver.find_element(By.XPATH, '//div[@class="Io6YTe fontBodyMedium kR99db "]')
                areas.append(area_element.text)
            except NoSuchElementException:
                areas.append('沒有顯示地點')

            #開放時間
            try:
                time_element = driver.find_element(By.XPATH, '//div[@class="t39EBf GUrTXd"]')
                times.append(time_element.get_attribute('aria-label'))
            except NoSuchElementException:
                times.append('沒有顯示開放時間')
            
            #點擊(第三層)
            try:
                btn = driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[3]/div/div/button[2]')
                btn.click()
                sleep(1)
            except NoSuchElementException as e:
                print(f"Button not found for {href}: {e}")

            # 個別星數
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, 'tr.BHOKXe[aria-label]')
                merged_star = "".join([element.get_attribute('aria-label') + ', ' for element in elements]).rstrip(', ')
                stars.append(merged_star)
            except NoSuchElementException as e:
                stars.append('沒有星數或評論')


            # tag
            try:
                tags = driver.find_elements(By.CSS_SELECTOR, 'span.uEubGf.fontBodyMedium')
                merged_tags = "".join([tag.text + ', ' for tag in tags]).rstrip(', ')
                tag.append(merged_tags)
            except NoSuchElementException as e:
                tag.append('沒有標籤')
            
        except Exception as e:
            areas.append('錯誤')
            times.append('錯誤')
            stars.append('錯誤')
            tag.append('錯誤')

    return areas, times, stars, tag

# Example usage
# driver = webdriver.Chrome() # Or any other browser driver
# hrefs = ["http://example.com"] # Replace with actual hrefs
# areas, times = extract_additional_info(driver, hrefs)

def extract_lat_long(url):
    try:
        lat_long_match = re.search(r'!3d([-\d.]+)!4d([-\d.]+)', url)
        if lat_long_match:
            return lat_long_match.group(1), lat_long_match.group(2)
        return None, None
    except Exception as e:
        print(f"extract_lat_long _ An error occurred: {e}")
        return None, None

# Example usage
# url = "https://www.google.com/maps/place/Location@!3d40.748817!4d-73.985428"
# latitude, longitude = extract_lat_long(url)

def extract_rating_reviews(rating_reviews):
    try:
        # 遇到"沒有評論"的資料，星數、評論數量 回傳 None (用字串才能成功寫入CSV?)
        if rating_reviews == '沒有評論':
            return 'None', 'None'

        parts = rating_reviews.split(' ')
        rating = parts[0]
        reviews = parts[2].replace(',', '').replace('"', '')  # Remove commas and quotes
        reviews = float(reviews)  # Convert string to float

        if reviews.is_integer():
            reviews = str(int(reviews))
        else:
            reviews = str(reviews)
        return rating, reviews
    except Exception as e:
        print(f"extract_rating_reviews error occurred: {e}")
        return None, None


def parse_reviews(review_string):
    try:
        pattern = r'(\d) 星級、([\d,]+) 則評論'

        review_counts = {'5星': 0, '4星': 0, '3星': 0, '2星': 0, '1星': 0}
        review_list = review_string.split(', ')
        for review in review_list:
            matches = re.findall(pattern, review)

            for match in matches:
                star, count = match
                count = int(count.replace(',', ''))
                review_counts[f'{star}星'] += count

        return review_counts
    except Exception as e:
        print(f"parse review _ An error occurred: {e}")
        return None

# Example usage
# review_string = "5 星級、1,234 則評論 4 星級、567 則評論"
# review_counts = parse_reviews(review_string)




def save_to_json(attractions, line):
    attractions_json = []

    for attraction in attractions:
        if len(attraction) == 8:
            name, url, total_star_and_comments, address, opening_hours, star_and_comments, time, tags = attraction
        elif len(attraction) == 7:
            name, url, total_star_and_comments, address, opening_hours, star_and_comments, tags = attraction
        else:
            continue  # 或者處理其他情況

        if total_star_and_comments == "店內購物":
            continue

        # Extract rating and total reviews
        star, total_comments = extract_rating_reviews(total_star_and_comments)

        # Parse reviews for each star rating
        parsed_reviews = parse_reviews(star_and_comments)

        # Extract latitude and longitude
        lat, lng = extract_lat_long(url)

        # Construct the JSON object
        attraction_data = {
            '景點名稱': name,
            '地址': address,
            'Google評論網址': url,
            '星數': star,
            '營業時間': opening_hours,
            '評論數量': total_comments,
            '緯度': lat,
            '經度': lng,
            'tag': tags,
            '5星評論數': parsed_reviews['5星'],
            '4星評論數': parsed_reviews['4星'],
            '3星評論數': parsed_reviews['3星'],
            '2星評論數': parsed_reviews['2星'],
            '1星評論數': parsed_reviews['1星']
        }

        attractions_json.append(attraction_data)

    line = line.strip()

    with open(f'{line}.json', 'w', encoding='utf-8') as json_file:
        json.dump(attractions_json, json_file, ensure_ascii=False, indent=4)



if __name__ == "__main__":
    driver = initialize_browser()
    processed_locations = set()  # 用集合來記錄已處理的地點

    with open('要抓的地點.txt', 'r', encoding='utf-8') as clocation:
        lines = clocation.readlines()
        for line in lines:
            line = line.strip()  # 移除開頭和結尾的空白字符
            if line in processed_locations:
                print(f"地點 '{line}' 已經處理過，跳過重複抓取。")
                continue

            navigate_to_google_maps(driver, line)
            scroll_page(driver)
            attractions_info = extract_attractions_info(driver)
            hrefs = [info[1] for info in attractions_info]
            areas, times, stars, tag = extract_additional_info_stars_and_tags(driver, hrefs)
            attractions = [info + (area, time, stars, tag) for info, area, time, stars, tag in
                           zip(attractions_info, areas, times, stars, tag)]

            save_to_json(attractions, line)
            
            processed_locations.add(line)  # 將已處理的地點加入集合中

    driver.quit()
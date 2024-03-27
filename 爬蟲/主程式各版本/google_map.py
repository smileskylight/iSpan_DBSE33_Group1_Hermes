from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import json

def initialize_browser():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--incognito")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-notifications")
    options.add_argument("--lang=zh-TW")

    driver = webdriver.Chrome(options=options)
    return driver

def navigate_to_google_maps(driver, query):
    driver.get("https://www.google.com/maps/")
    search_element = driver.find_element(By.CSS_SELECTOR, "input#searchboxinput.searchboxinput.xiQnY")
    search_element.send_keys(query)
    search_element.send_keys(Keys.ENTER)
    sleep(2)
    search_element.send_keys(Keys.BACKSPACE,Keys.BACKSPACE,Keys.BACKSPACE)
    search_element.send_keys("旅遊景點")
    search_element.send_keys(Keys.ENTER)
    sleep(1)

def scroll_page(driver):
    times = input('請輸入你要向下滾幾次(數字) : ')
    target_element = driver.find_element(By.XPATH, '//*[@class="m6QErb DxyBCb kA9KIf dS8AEf ecceSd" and @role="feed"]')
    driver.execute_script("arguments[0].scrollTo({ top: arguments[0].scrollTop + 200, behavior: 'smooth' });", target_element)
    sleep(3)

    for _ in range(times):
        driver.execute_script("arguments[0].scrollTo({ top: arguments[0].scrollTop + 800, behavior: 'smooth' });", target_element)
        sleep(3)

def extract_attractions_info(driver):
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.qBF1Pd.fontHeadlineSmall')))
    titles = [element.text for element in driver.find_elements(By.CSS_SELECTOR, '.qBF1Pd.fontHeadlineSmall')]

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.hfpxzc')))
    hrefs = [element.get_attribute("href") for element in driver.find_elements(By.CSS_SELECTOR, 'a.hfpxzc')]

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//span[@aria-label]')))
    star_and_comment_elements = driver.find_elements(By.XPATH, '//span[@aria-label]')[1:]  # Skip the first element
    star_and_comments = [element.get_attribute("aria-label") for element in star_and_comment_elements]

    return list(zip(titles, hrefs, star_and_comments))

def extract_additional_info(driver, hrefs):
    areas = []
    times = []
    five_start_and_commends = []
    locationtags = []
    
    for href in hrefs:
        driver.get(href)
        sleep(0.5)

        try:
            area_element = driver.find_element(By.XPATH, '//div[@class="Io6YTe fontBodyMedium kR99db "]')
            areas.append(area_element.text)
        except NoSuchElementException:
            areas.append('沒有顯示地點')

        try:
            time_element = driver.find_element(By.XPATH, '//div[@class="t39EBf GUrTXd"]')
            times.append(time_element.get_attribute('aria-label'))
            sleep(2)
        except NoSuchElementException:
            times.append('沒有顯示開放時間')
            sleep(2)
            
        try:
            btn = driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[3]/div/div/button[2]')
            btn.click()     
            elements = driver.find_elements(By.CSS_SELECTOR, 'tr.BHOKXe[aria-label]')
            merged_star = ""  
            for element in elements:
                aria_label_value = element.get_attribute('aria-label') 
                merged_star += aria_label_value + ', '
            merged_string = merged_star.rstrip(', ')
            five_start_and_commends.append(merged_string)
        except NoSuchElementException as e:
            five_start_and_commends.append('沒有星數')  
        
        try:
            tags = driver.find_elements(By.CSS_SELECTOR, 'span.uEubGf.fontBodyMedium')
            merged_tags = ""
            for tag in tags:
                merged_tag = tag.text
                merged_tags += merged_tag + ', '
            locationtags.append(merged_tags)
            sleep(2)
        except NoSuchElementException as e:
            print(f"Error in grabbing tags: {e}")
            locationtags.append('沒有標籤')
            sleep(2)                         
                   
    return areas, times,five_start_and_commends,locationtags

def save_to_file(attractions):
    with open('小琉球景點new.txt', 'a', encoding='utf-8') as file:
        json.dump(attractions, file, ensure_ascii=False)
        file.write('\n')

def main():
    driver = initialize_browser()
    try:
        location = input('請輸入地點(鄉鎮市區) : ')
        navigate_to_google_maps(driver, location)
        scroll_page(driver)
        attractions_info = extract_attractions_info(driver)
        hrefs = [info[1] for info in attractions_info]
        areas, times, five_start_and_commends, locationtags = extract_additional_info(driver, hrefs)
        attractions = [info + (area, time, five_start_and_commends, locationtags) for info, area, time, five_start_and_commends, locationtags in zip(attractions_info, areas, times, five_start_and_commends, locationtags)]
        save_to_file(attractions)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()

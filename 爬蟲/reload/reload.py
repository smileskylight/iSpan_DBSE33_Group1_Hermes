import pyautogui
import threading
from time import sleep
from IPython.display import clear_output


def listening():
    global switch  # 迴圈開關

    while switch:
        # 睡一下
        sleep(0.01)

        # 自動清除此格的文字輸出
        clear_output(wait=True)

        try:
            # 取得 Box 物件
            btn_reload = pyautogui.locateOnScreen(
                r'reload.png',
                confidence=0.9  # opencv信心指數，用 1 的話圖片一點灰塵污漬都不能有
            )  # 當前目錄放入重新載入圖片

            # 如果找到圖片，則執行點擊操作
            if btn_reload:
                print("Found reload button at:", btn_reload)  # 印出圖片位置

                # 圖片中心點位置
                btn_reload_point = pyautogui.center(btn_reload)

                # 按下 重新載入
                pyautogui.click(btn_reload_point.x, btn_reload_point.y)
            else:
                print("Reload button not found")  # 如果沒有捕獲到圖片，印出提示

        except KeyboardInterrupt:  # 捕獲按下 Ctrl+C 的異常
            print("Ctrl+C detected. Exiting...")
            switch = False  # 結束迴圈

        except Exception as e:
            pass


if __name__ == "__main__":
    switch = True
    listening_thread = threading.Thread(target=listening)  # 建立listening執行緒
    listening_thread.start()  # 啟動執行緒

    try:
#####主程式
        a = 0
        n = 1
        while a != 1:
            print(n)
            n += 1
            sleep(2)

#####主程式
    except KeyboardInterrupt:  # 捕獲按下 Ctrl+C 的異常
        print("Ctrl+C detected. Exiting...")
        switch = False  # 結束迴圈



    switch = False  # 爬蟲結束，結束迴圈
    listening_thread.join()  # 结束執行緒

 
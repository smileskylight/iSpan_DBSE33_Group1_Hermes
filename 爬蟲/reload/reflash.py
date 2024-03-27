# listening
import pyautogui
from time import sleep, time
import keyboard
from IPython.display import clear_output

# 多執行緒
import threading

def listening():
    global switch #迴圈開關

    while switch:
        # 睡一下
        sleep(0.01)

        #自動清除此格的文字輸出
        clear_output(wait=True)

        try:
            # 取得 Box 物件
            btn_reload = pyautogui.locateOnScreen(
                './reload.png',
                confidence=0.9 # opencv信心指數，用 1 的話圖片一點灰塵污漬都不能有 
            ) # 當前目錄放入重新載入圖片
						
						# 圖片中心點位置
            btn_reload_point = pyautogui.center(btn_reload) 

            # 按下 重新載入
            pyautogui.click(btn_reload_point.x, btn_reload_point.y)
        except:
            pass


if __name__ == "__main__":
    switch = True
    listening_thread = threading.Thread(target=listening) # 建立listening執行緒
    listening_thread.start()# 啟動執行緒
		'''
    
		爬蟲主程式

		'''
    switch = False # 爬蟲結束，結束迴圈   
    listening_thread.join() # 结束執行緒
    
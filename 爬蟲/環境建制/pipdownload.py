# 下載套件
def download():
    import sys
    import subprocess
    from time import sleep

    # 要檢查的套件列表
    required_packages = [
        're',
        'requests',
        'json',
        'os',
        'pprint',
        'bs4',
        'fake_useragent',
        'lxml',
        'selenium',
        'pandas',
        'pyautogui',
        'threading',
        'IPython',
        'opencv-python'
        # 添加其他套件的名稱
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print(f"缺少套件: {', '.join(missing_packages)}")
        req = input('是否下載套件 y/n : ')
        if req.lower() == 'y':
            subprocess.call(['pip', 'install'] + missing_packages)
        elif req.lower() == 'n':
            print('拒絕下載即將關閉程式')
            sleep(5)
            sys.exit()
    else:
        return       
download()
import re
import requests as rq
import json
import sys
import subprocess
import os
import lxml
import selenium
from pprint import pprint
from bs4 import BeautifulSoup as bs
from fake_useragent import UserAgent
from time import sleep
import pandas
import pyautogui
import threading
import IPython
import opencv


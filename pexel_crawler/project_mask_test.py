from selenium.webdriver import Chrome
from bs4 import BeautifulSoup
import requests
import os
import time


driver = Chrome(executable_path='./chromedriver')                   # 根據柏辰提供的https://segmentfault.com/a/1190000040450510
# set webdriver => undefined or false
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {   # 所記載的隱藏Selenium 黑科技寫法，讓Pexel防Selenium可以被破解
    "source": """
       Object.defineProperty(navigator, 'webdriver', {
         get: () => undefined
       })
     """
})


url = "https://www.pexels.com/zh-tw/search/%E5%8F%A3%E7%BD%A9/?page=1"       # target website
url_start = "https://www.pexels.com/zh-tw/search/%E5%8F%A3%E7%BD%A9/?page="  # for changing pages


def pic_catch(soup):                             # get the photos from pexels
    for a in soup.select("a.js-photo-link"):
        imageSrc = a.img["src"]
        image = requests.get(imageSrc)
        imageContent = image.content
        i = str(a["href"]).split("/")[3]         # name the photo from preprocessing the href

        path = f"{dir}/{i}.jpg"
        file = open(path, "wb")                  # save the photo
        file.write(imageContent)
        file.close()
        time.sleep(0.5)
        # print(i)

# the dir which storages the photo
dir = "Mask_data"
if not os.path.isdir(dir):
    os.makedirs(dir)


for p in range(2, 5):                 # crawl page.2 ~ page.4
    driver.get(url)                   # get the pages
    driver.maximize_window()
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")

    pos = 0                            # 網路找到的Selenium 下拉滾輪寫法，
    for x in range(4):
        pos += x * 500  # 每次下滾500
        js = "document.documentElement.scrollTop=%d" % pos
        driver.execute_script(js)
        time.sleep(1)

    pic_catch(soup)
    time.sleep(5)
    url = url_start + f"{p}"


driver.close()

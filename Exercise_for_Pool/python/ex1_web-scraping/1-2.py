from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import re
import pandas as pd
import time

options = Options()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')

options.add_argument("--headless")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0")
driver = webdriver.Chrome(options=options)

top_url="https://r.gnavi.co.jp/area/jp/izakaya/rs/"

def get_mail(driver,url):
    driver.get(url)
    time.sleep(3)
    text = driver.find_element(By.TAG_NAME,"body").text
    mail_match = re.search(r"[\w\.-]+@[\w\.-]+",text)
    if mail_match:
        return mail_match.group()
    return " "

def get_region(region):
    pattern=r"(.*?[都道府県])(.+?[市区町村])(.+?)(?=\d)([\d\-]+)?(.*)"
    m=re.match(pattern,region)
    if m:
        pref = m.group(1)
        city = m.group(2)
        ban = m.group(3)+m.group(4)
        building = m.group(5) or ""
        return pref,city,ban,building
    else:
        return "","","",""

def get_store_url(driver,url):
    try:
        driver.get(url)
        time.sleep(3)
        link = driver.find_element(By.XPATH,"//a[@title='オフィシャルページ']")
        href = link.get_attribute("href")
        driver.get(href)
        time.sleep(3)
        store_url = driver.current_url
        return store_url
    except:
        return ""

def check_ssl(driver,url):
    try:
        driver.get(url)
        time.sleep(3)
        final_url = driver.current_url
        return final_url.startswith("https://")
    except:
        return False
    
def scrape():
    driver.get(top_url)
    time.sleep(3)
    stores_list = []
    all_store_urls = []

    count=0

    while count < 50:
        stores = driver.find_elements(By.CLASS_NAME,"style_titleLink___TtTO")
        store_links = [s.get_attribute("href") for s in stores if s.get_attribute("href")]
        for url in store_links:
            all_store_urls.append(url)
            count += 1
            if count >= 50:
                break
        next_page = driver.find_element(By.XPATH,"//a[img[contains(@class,'style_nextIcon__Ad_pH')]]")
        next_page.click()
        time.sleep(3)
   
    for url in all_store_urls:
            driver.get(url)
            time.sleep(3)

            store_list=[]
            name = driver.find_element(By.ID,"info-name").text.strip()
            number = driver.find_element(By.CLASS_NAME,"number").text
            mail = get_mail(driver,url)
            region = driver.find_element(By.CLASS_NAME,"region").text
            pref,city,ban,building = get_region(region)
            store_url = get_store_url(driver,url)
            has_ssl = check_ssl(driver,store_url) if store_url else False
            store_list += [name,number,mail,pref,city,ban,building,store_url,has_ssl]
            stores_list.append(store_list)
    driver.quit()
    return stores_list

stores_list = scrape()
df = pd.DataFrame(
    stores_list,
    columns=["店舗名", "電話番号", "メールアドレス", "都道府県", "市区町村", "番地", "建物名", "URL", "SSL"]
    )
df.to_csv("1-2.csv",index=False,encoding="utf-8-sig")
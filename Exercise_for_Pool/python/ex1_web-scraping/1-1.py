import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import time


url="https://r.gnavi.co.jp/area/jp/izakaya/rs/"
next_url="https://r.gnavi.co.jp/area/jp/izakaya/rs/?p=2"
column=["店舗名","電話番号","メールアドレス","都道府県","市区町村","番地","建物名","URL","SSL"]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0"
}

response = requests.get(url,headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

def get_list(url):
    response=requests.get(url,headers=headers)
    soup = BeautifulSoup(response.text,"html.parser")
    content = soup.find_all("a",class_="style_titleLink___TtTO")
    link=[]
    for a_tag in content:
        href = a_tag.get('href')
        link.append(href)

    stores_list=[]
    for link_url in link:
        time.sleep(3)
        storelist=[]
        res=requests.get(link_url,headers=headers)
        res.encoding = res.apparent_encoding
        soup=BeautifulSoup(res.text,"html.parser")
        name=soup.find("h1",class_="shop-info__name").text.strip().replace('\xa0', '')
        number=soup.find("span",class_="number").text
        mail=get_mail(link_url)
        region=soup.find("span",class_="region").text
        pref,city,ban,building=region_se(region)
        storelist+=[name,number,mail,pref,city,f"'{ban}",building,"" ,""]
        stores_list.append(storelist)
    return stores_list


def get_mail(url):
    time.sleep(3)
    mail_response=requests.get(url,headers=headers)
    mail_soup=BeautifulSoup(mail_response.text,"html.parser")
    text=mail_soup.get_text()
    mail_match = re.search(r"[\w\.-]+@[\w\.-]+",text)
    if mail_match:
        return mail_match.group()
    return ""

def region_se(region):
    time.sleep(3)
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

stores_list=get_list(url)

if len(stores_list)<50:
    time.sleep(5)
    stores_list.extend(get_list(next_url))

data=[]
for store in stores_list:
    data.append(store) if len(data)<50 else ""

df = pd.DataFrame(data,columns=column)

df.to_csv("1-1.csv", index=False, encoding="utf-8-sig")
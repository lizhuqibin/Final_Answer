#!/usr/bin/env python
# coding: utf-8

# In[2]:


get_ipython().system('pip install bs4')
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import time


# In[23]:


url="https://r.gnavi.co.jp/area/jp/izakaya/rs/"
next_url="https://r.gnavi.co.jp/area/jp/izakaya/rs/?p=2"
column=["店舗名","電話番号","メールアドレス","都道府県","市区町村","番地","建物名","URL","SSL"]
stores_list=get_list(url)

if len(stores_list)<50:
    time.sleep(5)
    stores_list.extend(get_list(next_url))


# In[26]:


data=[]
data.append(column)
for store in stores_list:
    data.append(store) if len(data)<=50 else ""


# In[27]:


df = pd.DataFrame(data)

df.to_csv("sample.csv", index=False, encoding="utf-8-sig")


# In[18]:


def get_list(url):
    response=requests.get(url)
    soup = BeautifulSoup(response.text,"html.parser")
    content = soup.find_all("a",class_="style_titleLink___TtTO")
    link=[]
    for a_tag in content:
        href = a_tag.get('href')
        link.append(href)

    stores_list=[]
    for link_url in link:
        storelist=[]
        res=requests.get(link_url)
        res.encoding = res.apparent_encoding
        soup=BeautifulSoup(res.text,"html.parser")
        name=soup.find("h1",class_="shop-info__name").text.strip().replace('\xa0', '')
        number=soup.find("span",class_="number").text
        mail=" "
        region=soup.find("span",class_="region").text
        m=region_se(region)
        storelist+=[name,number,mail,m.group(1),m.group(2),m.group(3),m.group(4) if m.group(4) else" ",link_url,ssl(link_url)]
        stores_list.append(storelist)
    return stores_list


# In[7]:


def region_se(region):
    pattern="(...??[都道府県])(.{1,7}?[市区町村])(.+?)((\d+(?:-\d+)*))(.+)"
    m=re.match(pattern,region)
    return m


# In[12]:


import re
def ssl(shop_link):
    for tag in shop_link:
                
        if re.match(r'^https?://', url):   
            if url.startswith("https://"):
                 return("True")
            else:
                return("False")
            


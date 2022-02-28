#!/usr/bin/env python
# coding: utf-8

# Loading the libraries
import requests
from bs4 import BeautifulSoup
import time
import random
from tqdm.notebook import tqdm as tqdm

# Part a
page_url = "https://www.barnesandnoble.com/b/books/_/N-1fZ29Z8q8?Nrpp=40&page=1"

headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"}

search_page = requests.get(page_url, headers=headers)
page_info = BeautifulSoup(search_page.content, "html.parser")

# Part b
url_prefix = "https://www.barnesandnoble.com"
list_product_header = page_info.find_all("h3", class_ = "product-info-title")

list_product_urls = []
product_dict = dict()

for i, product in enumerate(list_product_header):
    
    product_url = url_prefix + product.find("a")['href']
    list_product_urls = list_product_urls + [product_url]
    
    product_name = product.find("a").text
    product_dict[i+1] = product_name

# Part c
base_fname = "top100_bn_"

for i, product_url in enumerate(list_product_urls):
    product_search = requests.get(product_url, headers=headers)

    fname = f"{base_fname}_{i+1}.html" 
    with open(fname,"a+") as f:
        f.write(str(product_search.content))
    f.close()
    
    # Adding sleep time
    sleep_time = random.randint(5,10)
    time.sleep(sleep_time)

# Part d
prod_count = len(list_product_header)

for i in range(prod_count):
    fname = f"{base_fname}_{i+1}.html"
    
    with open(fname, "r") as f: 
        page_content = BeautifulSoup(f, "html.parser")
    f.close()

    overview_box = page_content.find("div", class_ = "content overview-expandable-section")
    overview_content = overview_box.find("div", class_ = "overview-cntnt")
    print(f"Overview content for '{product_dict[i+1]}'")
    print(overview_content.text[:100])
    print("")
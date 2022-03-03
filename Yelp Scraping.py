#!/usr/bin/env python
# coding: utf-8

# In[32]:


import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import random
from tqdm.notebook import tqdm
import re


# In[8]:


page_var = ['0','10','20','30']
base_url = 'https://www.yelp.com/search?find_desc=donut+shop&find_loc=San+Francisco%2C+CA+94105&start='
base_fname = 'sf_donut_shop_search_page_'
headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"}


# In[19]:


page_ids = []
for page in tqdm(page_var):
    search_url = base_url + page
    
    page_id = str(int(int(page)/10 + 1))
    page_ids.append(page_id)
    
    search_response = requests.get(search_url, headers = headers)
    search_content = str(search_response.content)
    
    fname = base_fname + page_id + '.html'
    
    with open(fname, 'w') as f:
        f.write(search_content)
    f.close()
    
    time.sleep(random.randint(3,6))


# In[20]:


page_ids


# In[21]:


fname = base_fname + page_ids[0] + '.html'
fname


# In[22]:


with open(fname, 'r') as f:
    soup = BeautifulSoup(f, "html.parser")
f.close()


# In[81]:


url_prefix = 'https://www.yelp.com'
title = soup.find_all('span', class_ = 'css-1uq0cfn')
for elem in title:
    if elem.text[0].isdigit():
        clean_label = re.sub(r'\\[a-z0-9]{3}','',elem.text)
        shop_rank = clean_label.split('.')[0]
        shop_name = clean_label.split('.')[1]
        
        url = elem.find('a')['href']
        shop_url = url_prefix + str(url)
        
        sibling = elem.find_parent('div').find_parent('div').find_parent('div').find_next_sibling()
        
        reviews = sibling.find('span', class_ = 'reviewCount__09f24__tnBk4 css-1e4fdj9').text
        ratings = sibling.find('div', class_ = "i-stars__09f24__foihJ i-stars--regular-4__09f24__zkZZV border-color--default__09f24__NPAKY overflow--hidden__09f24___ayzG")['aria-label']
        
        sibling = sibling.find_next_sibling()

        tags = sibling.find_all('a')
        tags_list = []
    
        for item in tags:
            tag = item.find('p').text
            tags_list.append(tag)
            
        try:    
            price_range = sibling.find('span', class_ = 'priceRange__09f24__mmOuH css-18qxe2r').text
        except:
            price_range = ''
            
        parent = sibling.find_parent('div').find_parent('div').find_parent('div')
        
        try:
            takeout_box = parent.find('div', class_ = 'margin-t1-5__09f24__nx2jL border-color--default__09f24__NPAKY')
            dining_list = takeout_box.find('ul')

            dining = dict()
            for dining_option in dining_list:
                value = dining_option.find('div',class_='icon__09f24__a1_rF css-1v994a0 border-color--default__09f24__NPAKY')
                value = value.find('span')['aria-hidden']

                key = dining_option.find('span', class_ = 'label__09f24__hNq6C display--inline__09f24__c6N_k border-color--default__09f24__NPAKY')
                key = key.find('span').text

                dining[key] = value
                
            try:
                if takeout_box.find('div', class_ = 'arrange-unit__09f24__rqHTg border-color--default__09f24__NPAKY'):
                    order_yelp = 'True'
                else:
                    order_yelp = 'False'
            except:
                pass
                
        except:
            dining = dict()
        
        print (f'Shop Rank:{shop_rank}')
        print (f'Shop Name: {shop_name}') 
        print (f'Shop Url: {shop_url}')
        print (f'Ratings: {ratings}')
        print (f'Num Reviews: {reviews}')
        print (f'Tags:{tags_list}')
        print (f'Price Range:{price_range}')
        print (f'Dining:{dining}')
        print (f'Order Yelp: {order_yelp}')
        
        print('--------------------------------')


# In[ ]:





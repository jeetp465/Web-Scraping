#!/usr/bin/env python

# Loading the required libraries
import requests
from bs4 import BeautifulSoup
import time
import random
import re
from pymongo import MongoClient
import json

# Creating a connection to MongoDB
client = MongoClient('localhost', 27017)

# Creating/Accessing a database
donuts = client["donut_shop"]

# Creating/Accessing a collection
donut_shop = donuts["sf_donut_shops"]

# Declaring the pages variable to iterate over for fetching top 40 results
page_var = ['0','10','20','30']
base_url = 'https://www.yelp.com/search?find_desc=donut+shop&find_loc=San+Francisco%2C+CA+94105&start='

# Base filename to save the search pages
base_fname = 'sf_donut_shop_search_page_'

# Headers to pass with the GET request
headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"}

# Looping over page_var and fetching top 40 Donut Shops in San Francisco on Yelp 
page_ids = []
for page in page_var:
    # Modifying the search url
    search_url = base_url + page
    
    # Creating page_ids from the page search term
    page_id = str(int(int(page)/10 + 1))
    page_ids.append(page_id)
    
    # Fetching the search page for Donut Shops
    search_response = requests.get(search_url, headers = headers)
    search_content = str(search_response.content)
    
    # Defining filename to save the webpage
    fname = base_fname + page_id + '.html'
    
    with open(fname, 'w') as f:
        f.write(search_content)
    f.close()
    
    # Adding sleep time to mimic human browsing and avoid getting blocked from Yelp. 
    # Don't want to go through the trouble of requesting for a new IP address
    time.sleep(random.randint(3,6))

# Looping over saved pages to extract shop information
for page_id in page_ids: 
    fname = base_fname + page_id + '.html'
    
    with open(fname, 'r') as f:
        # Parsing the saved file into html
        soup = BeautifulSoup(f, "html.parser")
    f.close()
    
    # Defining a url prefix to append to the shop urls
    url_prefix = 'https://www.yelp.com'
    
    # Identifying all the titles on the search page
    title = soup.find_all('span', class_ = 'css-1uq0cfn')
    
    # Looping over all the identified titles
    for elem in title:
        # Differentiating the result as per recommended sorting from the 
        # sponsored result.
        if elem.text[0].isdigit():
            # Defining a document to insert into MongoDB Collection.
            shop_info = dict()
            
            # Cleaning the label and extracting shop rank and shop name from it.
            clean_label = re.sub(r'\\[a-z0-9]{3}','',elem.text)
            shop_rank = clean_label.split('.')[0]
            shop_name = clean_label.split('.')[1]
            
            # Adding shop rank and shop name to the shop_info document
            shop_info['Rank'] = shop_rank
            shop_info['Name'] = shop_name
            
            # Extracting the shop url and appending the url prefix defined earlier
            url = elem.find('a')['href']
            shop_url = url_prefix + str(url)
            
            # Adding shop url to shop_info document
            shop_info['Url'] = shop_url
            
            # Identified the common siblings to go to the next line for fetching
            # number of reviews and the rating of the shop
            sibling = elem.find_parent('div').find_parent('div').find_parent('div').find_next_sibling()
            
            # Fetching and adding the number of reviews to shop_info document
            reviews = sibling.find('span', class_ = 'reviewCount__09f24__tnBk4 css-1e4fdj9').text
            shop_info['Reviews'] = int(reviews)
            
            # Fetching and adding the the rating to shop_info document
            class_id = re.search('i-stars[_A-Z0-9a-z -]*"',str(sibling))[0][:-1]
            ratings = sibling.find('div', class_ = class_id)['aria-label']
            shop_info['Rating'] = float(ratings.split(' ')[0])
            
            # Fetching the next sibling to identify the price range and the tags associated with a shop
            sibling = sibling.find_next_sibling()
    
            # Dynamically maintaing tags.
            # Need to account for no tags. 
            tags = sibling.find_all('a')
            tags_list = []
        
            for item in tags:
                tag = item.find('p').text
                tags_list.append(tag)
                
            # Adding the tags to the shop_info document
            shop_info['Tags'] = tags_list
                
            # Fetching the price range mentioned as '$', '$$', '$$$' for the shops
            # Try-Catch loop to account for missing '$'*
            try:    
                price_range = sibling.find('span', class_ = 'priceRange__09f24__mmOuH css-18qxe2r').text
            except:
                price_range = ''
                
            # Adding the price range to shop info document
            shop_info['Price_Range'] = price_range
                
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
                order_yelp = 'False'
                
            # Adding dining options to the shop_info document
            shop_info['Dining'] = dining
            
            # Adding Ordering Bool to shop_info document
            shop_info['Order_Yelp'] = order_yelp
            
            print (shop_info)
            print('--------------------------------')
            donut_shop.insert(shop_info)
            
print("Fetched Basic Details of Top 40 Donut Shops")
            
# Querying the url saved from MongoDB for all stores
filter_ = {}
fields = {"Url" : 1,
          "Rank" : 1
          }
# We pass both the filter criteria and the relevant fields to the find query
query_out = donut_shop.find(filter_, fields)

# Storing the query output into a dictionary
rank_url_dict = dict()
for result in query_out:
    rank_url_dict[result['Rank']] = result['Url']
            
# Fetching the shop pages of all the urls and saving it in a local copy
base_fname = 'sf_donut_shop_'
for key, value in rank_url_dict.items():
    
    search_page = requests.get(value, headers = headers)
    search_content = str(search_page.content)
    
    fname = base_fname + str(key) + '.html'
    
    with open(fname, 'w') as f:
        f.write(search_content)
    f.close()
    
    time.sleep(random.randint(4,6))
    
# Iteration over each Shop to fetch phone number, address and website
# Maintaining the new store information in a dictionary
new_info = dict()
for key in list(rank_url_dict.keys()):
    # Dynamically maintaining filename
    fname = base_fname + str(key) + '.html'
    
    # Parsing the data into html format
    with open(fname, 'r') as f:
        soup = BeautifulSoup(f, "html.parser")
    f.close()

    # Maintaining the new fetched information in a dict
    shop_data = {}

    # Identifying the right box to fetch phone number, address and website
    box = soup.find('div', class_ = "css-xp8w2v padding-t2__09f24__Y6duA padding-r2__09f24__ByXi4 padding-b2__09f24__F0z5y padding-l2__09f24__kf_t_ border--top__09f24__exYYb border--right__09f24__X7Tln border--bottom__09f24___mg5X border--left__09f24__DMOkM border-radius--regular__09f24__MLlCO background-color--white__09f24__ulvSM")

    # Adding a try-catch statement to control for absence of Websites and Phone Number
    try:
        # Identifying list of elements corresponding to Website and Phone
        web_phone_identifier = box.find_all('p', class_ = 'css-na3oda')
        
        for elem in web_phone_identifier:
            # Fetching the parent element to fetch Phone Number and Website 
            # depending on the text of the common element
            parent = elem.find_parent('div')
            
            # When common element corresponds to Phone Number
            if elem.text == 'Phone number':
                phone = parent.find('p', class_ = "css-1p9ibgf")
                shop_data["Phone"] = phone.text
            # When common element corresponds to Website
            elif elem.text == 'Business website':
                website = parent.find('a', class_ = 'css-1um3nx')['href']
                shop_data["Website"] = url_prefix + website
    except:
        pass

    try:
        address = box.find('p', class_="css-qyp8bo").text
        shop_data["Address"] = address
    except:
        pass

    print(shop_data)
    print('---------')
    
    # Mapping the new shop data into dict using Shop Rank
    new_info[key] = shop_data
            
print("Fetched Additional Details of Top 40 Donut Shops")

# Making API call to https://www.positionstack.com to obtain lat, long from a given address
base_api = "http://api.positionstack.com/v1/forward?access_key=02709fbfcb98604117f8d866ee0c3fdb&query="

for key in new_info.keys():
    try:
        # Fetching the address from the new shop information
        address = new_info[key]['address']
        
        # Creating the search url 
        api_url = base_api + address
        
        api_response = requests.get(api_url, headers=headers)
        api_content = api_response.content
        
        json_response = json.loads(api_content)
        
        # Appending the Lat, Long information to the address, phone number and website
        new_info[key]['latitude'] = json_response['data'][0]['latitude']
        new_info[key]['longitude'] = json_response['data'][0]['longitude']
    except:
        pass
    
    # Updating the newly fetched information to collection
    donut_shop.update_many({"Rank":str(key)},{"$set": new_info[key]})
    
    # Adding a sleep time
    time.sleep(random.randint(4,6))

# Checking existing index on the collection
print (donut_shop.index_information())

# Creating an index on the Rank column
donut_shop.create_index("Rank")

# Checking the index post setting the index on the Rank Column
print (donut_shop.index_information())

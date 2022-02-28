#!/usr/bin/env python
# coding: utf-8

import requests
import time
from bs4 import BeautifulSoup

username = "thestereotypicalgujju"
password = "J4495WSYcLzScCh"
headers = {"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"}

# Creating a session to make get and post requests
session = requests.session()

# Requesting login page using GET request
url = " https://www.planespotters.net/user/login"
page_info = session.get(url, headers=headers)

# Parsing the response into html code
login_page = BeautifulSoup(page_info.content, "html.parser")
form_box = login_page.find("div", class_ = "planespotters-form")

# Accessing the hidden value to be used in POST request
hidden_input = form_box.find_all("input", type = "hidden")
hidden_inputs = {}

# Parsing the hidden elements into a dictionary
for hidden_elem in hidden_input:
    try:
        hidden_inputs[hidden_elem['id']] = hidden_elem['value']
    except:
        hidden_inputs[hidden_elem['id']] = ''
        
# Accessing the cookies received in response to the GET request
cookies = page_info.cookies.get_dict()

# Creating dict for username and password
user_details = {"username": username,
                "password": password}

# Creating the POST response parameters
data = {**user_details, **hidden_inputs}

# Adding sleep before making another request
time.sleep(5)

# Making the POST request
res = session.post(url, 
                   data = data, 
                   headers = headers,
                   cookies = cookies,
                   timeout = 15)

# Accessing the cookies received in response to the POST request
cookies_new = res.cookies.get_dict()

# Combining both the cookies
cookies = {**cookies, **cookies_new}

# Adding sleep before making another request
time.sleep(5)

# Requesting Member Page using GET request
member_url = "https://www.planespotters.net/member/profile"
member_page = session.get(member_url,
                          headers = headers,
                          cookies = cookies)

# Parsing the member page
member_page_info = BeautifulSoup(member_page.content, 'html.parser')
print(member_page_info)
print(f"Cookies used: {cookies}")
print(f"Username was found in the MEMBER PROFILE PAGE: {bool(member_page_info.find(text=username))}")
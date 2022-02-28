#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Jeet Patel, Keshore Suryanarayanan, Ravi Kiran Bachu
"""

import requests
import json
import re
from datetime import datetime
from bs4 import BeautifulSoup
import time

# Defining the API Call parameters and the header
api_endpoint = "https://api.github.com/repos/apache/hadoop/contributors?per_page=100"
username = "jeetp465"
token = "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"
headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"}

# Starting a session with the authentication code
session = requests.Session()
session.auth = (username, token)

# ================================================================ #
# =========================    PART A    ========================= #
# ================================================================ #

# Making the API Call
api_call = session.get(api_endpoint)
response_text = api_call.text

# Parsing the API response into json
response_json = json.loads(response_text)

# Defining a dict to store the number of repos and their contributions
user = dict()

for i, elem in enumerate(response_json):
    # Defining a dict to store the number of repository and total contributions made by the user
    user_info = dict()
    
    user_id = elem["login"]
    user_url = elem["html_url"]
    
    # Getting the number of repository
    repository_endpoint = elem["repos_url"] + "?per_page=100"
    repo_api_call = session.get(repository_endpoint, headers=headers)
    repo_response_text = str(repo_api_call.text)
    repo_json = json.loads(repo_response_text)
    
    num_repos = len(repo_json)

    while 'next' in repo_api_call.links.keys():
        next_url = repo_api_call.links['next']['url']
        repo_api_call = session.get(next_url, headers=headers)
        next_repo_page_response = str(repo_api_call.text)
        next_repo_json = json.loads(next_repo_page_response)
        num_repos += len(next_repo_json)
        
    user_info['num_repos'] = num_repos
    
    # Fetching the profile page of the user
    user_profile = session.get(user_url, headers=headers)
    user_profile_content = BeautifulSoup(user_profile.content, "html.parser")
    
    # Fetching the list of years
    years_list = user_profile_content.find("ul", class_ = "filter-list small")
    years_list = years_list.find_all("li")
    
    # Defining num contribution to store the total contributions
    num_contribution = 0
    
    # Fetching contribution from each year
    for year in years_list:
        time.sleep(2)
        prefix = "https://www.github.com"
        year_url = prefix + year.find("a")['href']
        
        # Fetching the respective year
        user_profile_year = session.get(year_url, headers=headers)
        user_profile_content = BeautifulSoup(user_profile_year.content, "html.parser")
        
        # Fetching the number of contributions from the contribution graph
        try:
            contribution_header = user_profile_content.find("div", class_ = "js-yearly-contributions")
            contribution_text = contribution_header.find("h2").text
            
            # Extracting number of contributions from the contribution text
            contributions = int(contribution_text.split()[0].replace(',',''))
            num_contribution += contributions
        except:
            print(user_profile_content)
            print(contribution_header)

    # Updating the contribution count to the user_info dict            
    user_info['num_contribution'] = num_contribution
    
    user[user_id] = user_info
    print(f"User{i+1}: {user_id} :: {user[user_id]}")

# ================================================================ #
# =========================    PART B    ========================= #
# ================================================================ #

# The commits are in descending order. Hence the last and last - 100th commit will be the 
# first commit on the first page and first commit on the second page respectively

# Defining endpoints for the first and second page
last_commit_endpoint = "https://api.github.com/repos/apache/hadoop/commits?per_page=100&page=1"
last_100_commit_endpoint = "https://api.github.com/repos/apache/hadoop/commits?per_page=100&page=2"

# Making API call to the first page and parsing the response into json
last_commits_api_call = session.get(last_commit_endpoint, headers=headers)
last_commits_api_response = last_commits_api_call.text
last_commits_json = json.loads(last_commits_api_response)

# Making API call to the second page and parsing the response into json
last_100_commit_call = session.get(last_100_commit_endpoint, headers=headers)
last_100_commit_response = last_100_commit_call.text
second_last_commit_json = json.loads(last_100_commit_response)

# Defining the Date Format to parse the timestamps
date_format_str = '%Y-%m-%d %H:%M:%S'

# Extracting Timestamp from the last commit
last_commit_ts = last_commits_json[0]["commit"]["author"]["date"]
# Removing TZ from the timestamp
last_commit_ts = re.sub(r'[A-Z]+',' ', last_commit_ts).strip()
last_commit_ts = datetime.strptime(last_commit_ts, date_format_str)

last_100_commit_ts = second_last_commit_json[0]["commit"]["author"]["date"]
last_100_commit_ts = re.sub(r'[A-Z]+',' ', last_100_commit_ts).strip()
last_100_commit_ts = datetime.strptime(last_100_commit_ts, date_format_str)

# Converting the timestamp difference to seconds
Timestamp_difference = (last_commit_ts - last_100_commit_ts).total_seconds()

# Converting seconds to days, hours and minutes
days = Timestamp_difference // (60*60*24)
hours = (Timestamp_difference - (days*60*60*24)) // (60*60)
minutes = (Timestamp_difference - (days*60*60*24) - (hours*60*60)) // 60

print(f"The timestamp difference between last commit and last - 100th commit is {days} Days {hours} Hours {minutes} Minutes")
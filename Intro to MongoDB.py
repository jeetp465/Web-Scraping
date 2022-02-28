#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 26 01:53:58 2022

@author: jeet
"""

# Importing the required libraries
from pymongo import MongoClient

# Setting up the connection
client = MongoClient("mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false")
database = client["samples_pokemon"]
collection = database["samples_pokemon"]


# Question 1

query = {}

query["candy_count"] = {
    u"$gte": 14.0
}

projection = {}

projection["name"] = 1.0
projection["_id"] = 0.0

cursor = collection.find(query, projection = projection)
print("Question 1")
try:
    for doc in cursor:
        print(doc)
finally:
    client.close()


# Question 2

query = {}

query["num"] = {
    u"$in": [
        u"009",
        u"005"
    ]
}


projection = {}

projection["name"] = 1.0
projection["_id"] = 0.0

cursor = collection.find(query, projection = projection)
print("Question 2")
try:
    for doc in cursor:
        print(doc)
finally:
    client.close()

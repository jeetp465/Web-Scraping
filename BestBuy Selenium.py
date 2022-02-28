from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Getting bestbuy.com
driver.get("https://www.bestbuy.com")
time.sleep(5)

# Checking for the annoying pop-up
try:
    popup = driver.find_element(By.CSS_SELECTOR,"button[aria-label='Close']")
    popup.click()
    time.sleep(2)
except:
    pass

# Getting the Deal of the Day button and clicking on it
deal_of_the_day = driver.find_element(By.XPATH,"//a[text() = 'Deal of the Day']")
deal_of_the_day.click()

# Adding a time lag
time.sleep(5)

# Getting the remaining time
time_hours = driver.find_element(By.CSS_SELECTOR,"span[class='hours cdnumber']").text
time_minutes = driver.find_element(By.CSS_SELECTOR,"span[class='minutes cdnumber']").text
time_seconds = driver.find_element(By.CSS_SELECTOR,"span[class='seconds cdnumber']").text

print(f"The time remaining for deal of the day is {time_hours} hours {time_minutes} minutes {time_seconds} seconds")

# Getting the product and clicking on the link
product = driver.find_element(By.CSS_SELECTOR,"h1[class='heading product-title']")
product.click()
time.sleep(5)

# Finding the reviews
reviews = driver.find_element(By.CSS_SELECTOR,"span[class='c-reviews-v4 c-reviews order-2']")
reviews.click()
time.sleep(10)

# Savon
with open('bestbuy_deal_of_the_day.html','w') as f:
    f.write(driver.page_source)
    
driver.quit()
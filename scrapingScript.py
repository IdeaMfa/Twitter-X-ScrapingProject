import sys
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import hashlib
import subprocess
import psycopg2


# Hash function to create pseudo tweet id
def create_tweet_hash(tweet):
    # Using SHA-256 for consistent hashing
    hash_object = hashlib.sha256(tweet.encode())
    hash_value = hash_object.hexdigest()
    return hash_value


# Function to convert list to string
def convert(s):  
    new = "" 
    
    for x in s: 
        new += x
    
    return new 


# Function to convert value of the date-time html attribute in the appropriate way
"""
For example:
    "2022-09-22T22:18:16.000Z" -> (20220922, 221816)
"""
def date_time_to_int(string):
    date = []
    time = []
    flag = 0
    for char in string:
        if flag == 0:
            if char != "T":
                date.append(char)
            else:
                flag = 1
        else:
            if char != ".":
                time.append(char)
            else:
                break

    date_with_ints = []
    for d in date:
        try:
            int(d)
            date_with_ints.append(d)
        except ValueError:
            continue
    
    date_string = convert(date_with_ints)
    date_int = int(date_string)

    time_with_ints = []
    for t in time:
        try:
            int(t)
            time_with_ints.append(t)
        except ValueError:
            continue
    
    time_string = convert(time_with_ints)
    time_int = int(time_string)
    
    return date_int, time_int

# Give postgresql user password example: password = "123456"
password = "123456"

# Give postgresql port (5432 by default)
port = "5432"

# Extract data from data base
conn = psycopg2.connect(host="localhost",
                        dbname="postgres",
                        user="postgres",
                        password=password,
                        port=port)

# Define cursor
cursor = conn.cursor()

# Execute the query to get all rows in the table
cursor.execute("SELECT * FROM tweet_data")

data = cursor.fetchall()

# Extract the tweet_id values into a Python list

tweets_id_from_db_list = [tweet_id[1] for tweet_id in data]

URL = sys.argv[1]
print(sys.argv[1])

username = ""


# Get username from URL
slash_counter = 0
for char in URL:
    if slash_counter == 3:
        username += char
    if char == "/":
        slash_counter = slash_counter + 1

# Initialize a set to keep track of unique tweets
unique_tweets = []
unique_image_urls = []

# Initialize the webdriver
driver_location = 'C:\chormedriver\chromedriver.exe'
service = Service(executable_path=driver_location)

# Try to run driver if it gives Message: tab crashed, run the script again
driver = webdriver.Chrome(service=service)



# Get url into code
driver.get(URL)
time.sleep(3)

# Find the body element
element = driver.find_element(By.TAG_NAME, 'body')

# Initialize previous scroll position
prev_scroll_position = 0

scroll_stop_IDcheck_ = 0

# Loop of scrolling page
tweets = []
while True:
    element.send_keys(Keys.PAGE_DOWN)
    time.sleep(2)

    # Get the current scroll position
    current_scroll_position = driver.execute_script("return window.scrollY")

    # Check if scroll position has changed (reached the bottom)
    if current_scroll_position == prev_scroll_position:
        break
    
    # Update scroll position
    prev_scroll_position = current_scroll_position

    # Get the page source after scrolling
    respound = driver.page_source
    soup = BeautifulSoup(respound, "html.parser")

    # Find all tweets' article tags 
    tweets_ = soup.find_all("article", {"data-testid": "tweet"})

    # Get date-time value
    tw_date_time = []
    for i in range(len(tweets_)):
        # Locate the HTML element by its tag name
        time_element = tweets_[i].find('time')

        # Extract the value of the datetime attribute
        datetime_value_from_html = time_element['datetime'] if time_element else None
        datetime_value = date_time_to_int(datetime_value_from_html)

        tw_date_time.append([datetime_value[0], datetime_value[1], i])

    # Sort date-time value
    sorted_tw_date_time = sorted(tw_date_time, key=lambda x: (x[0], x[1]), reverse=True)

    index_list = []
    for sorted_tw_date_time_ in sorted_tw_date_time:
        index_list.append(sorted_tw_date_time_[2])

    # Reorder tweets_ list using the index list
    reordered_tweets_ = [tweets_[i] for i in index_list]

    for tweet_ in reordered_tweets_:
        if tweet_ not in tweets:
            tweets.append(tweet_)

    # Add tweets' article tags into the 2D list by checking if it exist in the table
    for tweet in tweets:
        # Check if the tweet's article tag in the list by using flag method
        flag = 0
        # Determine an ID for tweet by hashing the text
        tweet_id = create_tweet_hash(tweet.get_text(strip=True))

        #Determine tweet's date-time
        tweet_time_element = tweet.find('time')
        tweet_date_time = tweet_time_element['datetime'] if time_element else None

        for unique_tweets_id in tweets_id_from_db_list:
            if tweet_id == unique_tweets_id:
                scroll_stop_IDcheck_ = 1
                break
        
        if scroll_stop_IDcheck_ != 0:
            break

        for unique_tweet in unique_tweets:
            if tweet_id == unique_tweet["tweet_id"]:
                flag = 1
                break
        
        # If the article does not in the table put it into the corresponding list
        if flag == 0:
            # Extract tweet text
            tweet_text_ = tweet.find("div", {"data-testid": "tweetText"})
            try:
                tweet_text = tweet_text_.get_text(strip=True)
            except AttributeError:
                continue

            
            #Save tweets with their IDs
            unique_tweets.append({
            "tweet_id": tweet_id,
            "username": username,
            "date-time": tweet_date_time,
            "text": tweet_text
            })

            # Find the image tag attached to the tweet
            images = tweet.find_all("img")

            for image in images:
                image_url = image.get("src")
                if image_url:
                    unique_image_urls.append({
                        "tweet_id": tweet_id,
                        "username": username,
                        "date-time": tweet_date_time,
                        "image_url": image_url
                    })
                else:
                    unique_image_urls.append({
                        "tweet_id": tweet_id,
                        "username": username,
                        "date-time": tweet_date_time,
                        "image_url": None
                    })
    
    if scroll_stop_IDcheck_ != 0:
        break
    
# Close the driver
driver.quit()

print(f"Total unique tweets found: {len(unique_tweets)}")
print(f"Total images with None values: {len(unique_image_urls)}")

# Get new tweets into list
new_tweets = []
for unique_tweet in unique_tweets:
    # New tweet and image data to add
    new_tweet = {
        "tweet_id": unique_tweet['tweet_id'],
        "username": unique_tweet['username'],
        "date-time": unique_tweet['date-time'],
        "text": unique_tweet['text']
    }
    new_tweets.append(new_tweet)

# Get new images into list
new_images = []
for image_url in unique_image_urls:
    new_image = {
        "tweet_id": image_url["tweet_id"],
        "username": image_url['username'],
        "date-time": image_url['date-time'],
        "image_url": image_url["image_url"]
    }
    new_images.append(new_image)

# Insert new tweets into the table
for tweet_data in new_tweets:
    if tweet_data["tweet_id"] not in tweets_id_from_db_list:
        cursor.execute(
        "INSERT INTO tweet_data (tweet_id, username, date_time, tweet_text) VALUES (%s, %s, %s, %s)",
        (tweet_data["tweet_id"], tweet_data["username"], tweet_data["date-time"], tweet_data["text"])
    )

# Insert new images into the table
for tweet_data in new_images:
    if tweet_data["tweet_id"] not in tweets_id_from_db_list:
        cursor.execute(
        "INSERT INTO tweet_data_media (tweet_id, username, date_time, tweet_image_url) VALUES (%s, %s, %s, %s)",
        (tweet_data["tweet_id"], tweet_data["username"], tweet_data["date-time"], tweet_data["image_url"])
    )

# Commit the queries
conn.commit()

# Close cursor and connection
cursor.close()
conn.close()
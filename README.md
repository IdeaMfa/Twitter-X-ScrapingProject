# Twitter-X-ScrapingProject
This project is designed to scrape tweets and associated images from Twitter (X) using Python, Selenium, and PostgreSQL. The project extracts tweet data, such as tweet text, date-time, and media (if available), and stores it in a PostgreSQL database.

## Features
- Selenium-based Web Scraping: Automatically scrolls Twitter (X) pages to extract tweets and media content.
- PostgreSQL Integration: Stores tweet data and media URLs in a PostgreSQL database.
- Duplicate Check: Prevents duplicate entries by comparing tweet IDs using SHA-256 hashing.
- Dynamic URL Handling: Fetches Twitter (X) profile URLs from the database and scrapes them.
- Date-Time Conversion: Converts date-time attributes to integers for easier database management.

```bash
Twitter(X)ScrapingProject/
│
├── main.py                    # Entry point for fetching URLs from the DB and running the scraper
├── scrapingScript.py           # Handles web scraping and data processing for each Twitter profile
├── README.md                   # Documentation
├── requirements.txt            # Python dependencies
└── database.sql                # SQL script to create necessary tables in PostgreSQL

```

## Requirements
- Python 3.x
- PostgreSQL
- Selenium
- Chrome WebDriver

## Installation
1. Clone this repository:
- Copy code
```bash
https://github.com/IdeaMfa/Twitter-X-ScrapingProject.git
```
2. Install the required Python packages:
```bash
pip install -r requirements.txt
```
3. Install PostgreSQL and create the necessary tables using the provided database.sql script.
4. Download and set up Chrome WebDriver from here.

## Configuration
1. Update the password and port values for PostgreSQL in both main.py and scrapingScript.py.
2. Ensure the correct path for the Chrome WebDriver is set in scrapingScript.py:
```python
driver_location = 'C:\\chromedriver\\chromedriver.exe'
```
## Usage
1. Populate the target_page_urls table in your PostgreSQL database with the Twitter profile URLs you want to scrape.
2. Run the main.py script:
Copy code
```bash
python main.py
```
3. This will fetch the URLs from the database and invoke scrapingScript.py for each URL.
4. The scraped data, including tweet texts and media URLs, will be stored in the tweet_data and tweet_data_media tables in your PostgreSQL database.

## Database Structure

### `target_page_urls`
Stores the Twitter (X) profile URLs to be scraped.

- **Columns:**
  - `url`: The URL of the Twitter (X) profile.

### `tweet_data`
Stores the tweet information scraped from Twitter (X).

- **Columns:**
  - `tweet_id`: Unique ID for each tweet (hashed using SHA-256).
  - `username`: Twitter handle of the account that posted the tweet.
  - `date_time`: Date and time of the tweet.
  - `tweet_text`: The text content of the tweet.

### `tweet_data_media`
Stores the media (images) associated with the tweets.

- **Columns:**
  - `tweet_id`: The corresponding tweet's ID.
  - `username`: Twitter handle of the account that posted the tweet.
  - `date_time`: Date and time of the tweet.
  - `tweet_image_url`: URL of the image attached to the tweet (if available).


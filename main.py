import subprocess
import psycopg2

args = []

# Define the arguments to pass to the script:
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

# Get the urls from DB
cursor.execute("SELECT url FROM target_page_urls")

# Fetch the cursor
data = cursor.fetchall()

# Extract the url values into a Python list
urls = [url[0] for url in data]

# Run the script with the arguments
for arg in urls:
    subprocess.run(["python", "scrapingScript.py", arg])

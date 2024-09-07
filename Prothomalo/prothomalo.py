import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv
from newsplease import NewsPlease
from datetime import datetime, timedelta

# Define the date range for filtering
start_date = datetime.strptime('2024-01-01', '%Y-%m-%d')
end_date = datetime.strptime('2024-06-27', '%Y-%m-%d')

# Generate a list of dates within the range
date_list = [(start_date + timedelta(days=x)).strftime('%Y-%m-%d') for x in range((end_date - start_date).days + 1)]

# Initialize lists to store the extracted data
locs = []
dates = []

# Iterate through each date and construct the sitemap URL
for date_str in date_list:
    sitemap_url = f'https://www.prothomalo.com/sitemap/sitemap-daily-{date_str}.xml'
    try:
        source = requests.get(sitemap_url).text
        soup = BeautifulSoup(source, 'xml')
        for url in soup.find_all('url'):
            loc = url.find('loc').text
            lastmod = url.find('lastmod').text
            locs.append(loc)
            dates.append(lastmod)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching sitemap for date {date_str}: {e}")
        continue

# Create a pandas DataFrame with the extracted data
data = {
    'URL': locs,
    'Last Modified Date': dates
}

data_links = pd.DataFrame(data)

# Write the header of the CSV file
csv_file = open('data.csv', 'w', newline='', encoding='utf-8')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Date Published', 'Headline', 'Article Body'])

# Function to scrape articles
def scrap_data_using_json_schema(pages_df):
    articles_scraped = 0
    for index, row in pages_df.iterrows():
        page = row['URL']
        article = NewsPlease.from_url(page)
        article_body = article.maintext
        date_published = article.date_publish
        headline = article.title
        
        csv_writer.writerow([date_published, headline, article_body])
        
        articles_scraped += 1
        print(f"Scraped article {articles_scraped}: {headline}")
    
    return "ok"

scrap_news = scrap_data_using_json_schema(data_links)
csv_file.close()

# Load the dataset to verify
dataset = pd.read_csv("data.csv")
print(dataset) 

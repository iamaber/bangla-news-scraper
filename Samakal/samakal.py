import requests
import pandas as pd
from newsplease import NewsPlease
from bs4 import BeautifulSoup
import newspaper
from datetime import datetime, timedelta
import time
import csv
import random
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Disable SSL warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Constants for user agents and file paths
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
]

CSV_FILE_PATH = 'data.csv'

# Function to get a random user agent
def get_random_user_agent():
    return random.choice(USER_AGENTS)

# Function to generate a list of dates
def generate_date_list(start_date, end_date):
    return [(start_date + timedelta(days=x)).strftime('%Y-%m-%d') for x in range((end_date - start_date).days + 1)]

# Function to fetch sitemap and extract URLs
def fetch_sitemap_urls(date_list):
    locs, dates = [], []
    session = requests.Session()
    session.verify = False
    
    for date_str in date_list:
        sitemap_url = f'https://samakal.com/sitemap/sitemap-daily-{date_str}.xml'
        headers = {'User-Agent': get_random_user_agent()}
        
        try:
            response = session.get(sitemap_url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'xml')
            
            for url in soup.find_all('url'):
                locs.append(url.find('loc').text)
                dates.append(url.find('lastmod').text)
            
            print(f"Processed sitemap for date {date_str}")
            time.sleep(random.uniform(1, 3))  # Random delay between requests
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching sitemap for date {date_str}: {e}")
            continue
    
    return pd.DataFrame({'URL': locs, 'Last Modified Date': dates})

# Function to scrape article data
def scrape_articles(pages_df, csv_writer):
    articles_scraped = 0
    
    for index, row in pages_df.iterrows():
        page = row['URL']
        
        try:
            article = newspaper.Article(page, language='bn')
            article.download()
            article.parse()
            
            article_body = article.text
            date_published = article.publish_date
            article_meta = NewsPlease.from_url(page)
            headline = article_meta.title
            
            if article_body and date_published and headline:
                csv_writer.writerow([date_published, headline, article_body])
                articles_scraped += 1
                print(f"Scraped article {articles_scraped}: {headline}")
            else:
                print(f"Skipped article {page}: Missing data")
        
        except Exception as e:
            print(f"Error scraping article {page}: {e}")
    
    return articles_scraped

# Main execution block

# Set date range
start_date = datetime.strptime('2024-08-05', '%Y-%m-%d')
end_date = datetime.now() - timedelta(days=1)  # Yesterday

# Generate date list
date_list = generate_date_list(start_date, end_date)

# Fetch sitemap URLs
data_links = fetch_sitemap_urls(date_list)

# Write to CSV
with open(CSV_FILE_PATH, 'w', newline='', encoding='utf-8') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['Date Published', 'Headline', 'Article Body'])
    
    # Scrape articles
    articles_scraped = scrape_articles(data_links, csv_writer)

print(f"Total articles scraped: {articles_scraped}")


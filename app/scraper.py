import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timezone
import os

def scrape_aljazeera_arabic():
    url = "https://www.aljazeera.net/news"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    articles = []
    for item in soup.find_all('h3', class_='gc__title'):
        title = item.get_text(strip=True)
        link = item.find('a')['href']
        article = {
            'title': title,
            'link': "https://www.aljazeera.net" + link,
            'source': 'Al Jazeera Arabic',
            'date_collected': datetime.now(timezone.utc).isoformat()
        }
        articles.append(article)

    # Create output directory if it doesn't exist
    output_dir = 'data/raw'
    os.makedirs(output_dir, exist_ok=True)

    # Save to CSV
    output_file = os.path.join(output_dir, 'aljazeera_arabic.csv')
    df = pd.DataFrame(articles)
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"✅ Scraped {len(df)} articles and saved to {output_file}")
    return df

if __name__ == "__main__":
    scrape_aljazeera_arabic()

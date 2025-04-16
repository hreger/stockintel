import requests
from bs4 import BeautifulSoup
import json
from typing import Dict, Optional
import re

class CompanyScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def get_wikipedia_data(self, company_name: str) -> Dict:
        """Fetch company information from Wikipedia"""
        try:
            search_url = f"https://en.wikipedia.org/wiki/{company_name.replace(' ', '_')}"
            response = requests.get(search_url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract company information
            info = {}
            
            # Get company description
            description = soup.find('div', {'class': 'mw-parser-output'})
            if description:
                first_paragraph = description.find('p')
                if first_paragraph:
                    info['description'] = first_paragraph.get_text().strip()
            
            # Get key information from infobox
            infobox = soup.find('table', {'class': 'infobox'})
            if infobox:
                for row in infobox.find_all('tr'):
                    header = row.find('th')
                    data = row.find('td')
                    if header and data:
                        info[header.get_text().strip()] = data.get_text().strip()
            
            return info
        except Exception as e:
            print(f"Error fetching Wikipedia data: {str(e)}")
            return {}
    
    def get_reuters_data(self, symbol: str) -> Dict:
        """Fetch company information from Reuters"""
        try:
            url = f"https://www.reuters.com/companies/{symbol}"
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            info = {}
            
            # Extract key metrics
            metrics = soup.find_all('div', {'class': 'KeyMetrics'})
            for metric in metrics:
                label = metric.find('div', {'class': 'label'})
                value = metric.find('div', {'class': 'value'})
                if label and value:
                    info[label.get_text().strip()] = value.get_text().strip()
            
            return info
        except Exception as e:
            print(f"Error fetching Reuters data: {str(e)}")
            return {}
    
    def get_company_profile(self, symbol: str, company_name: str) -> Dict:
        """Get comprehensive company profile by combining data from multiple sources"""
        profile = {
            'symbol': symbol,
            'name': company_name,
            'wikipedia': self.get_wikipedia_data(company_name),
            'reuters': self.get_reuters_data(symbol)
        }
        
        return profile

if __name__ == "__main__":
    # Example usage
    scraper = CompanyScraper()
    profile = scraper.get_company_profile('AAPL', 'Apple Inc.')
    print(json.dumps(profile, indent=2)) 
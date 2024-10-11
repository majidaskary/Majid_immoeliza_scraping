# immoweb_scraper.py

# Importing the same necessary libraries as your original code.
import requests 
from bs4 import BeautifulSoup  
import pandas as pd  
import math  


class all_links_scraper:
    def __init__(self, output_dir, num_pages=1):
        # Initialization method (same as before, just wrapped in a class)
        self.output_dir = output_dir  
        self.num_pages = num_pages  
        # Changed: sale_link now points to page 1 (as corrected)
        self.sale_link = 'https://www.immoweb.be/en/search/house-and-apartment/for-sale?countries=BE&page=1&orderBy=relevance'
        self.headers = {  
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }

    # generating page links
    def generate_page_links(self):
        # generate links for each page
        group_pages_link_sale = [self.sale_link]  
        for p in range(2, self.num_pages + 1): 
            group_pages_link_sale.append(self.sale_link + "&page=" + str(p))  
        return group_pages_link_sale  

    # extracting links from group pages
    def scrape_links(self):
        group_pages_link_sale = self.generate_page_links()  
        all_links = []  

        for l in group_pages_link_sale:  
            session = requests.Session()  
            response = session.get(l, headers=self.headers)  
            soup = BeautifulSoup(response.text, 'html.parser')  

            # extracting all 'href' from 'a' tags 
            for tag_a in soup.find_all('a', class_="card__title-link", href=True):  
                all_links.append(tag_a['href'])  

        unique_links = set(all_links)  
        return [link for link in unique_links if "/new-real-estate-project-" not in link]  

    # saveing the links in CSV files
    def save_links_to_csv(self, filtered_links, num_files=10):
        # dividing links to multiple files
        links_per_file = math.ceil(len(filtered_links) / num_files) 

        for i in range(num_files):  
            start_index = i * links_per_file  
            end_index = min((i + 1) * links_per_file, len(filtered_links))  
            links_part = filtered_links[start_index:end_index]  

            # save each part to a separate CSV file 
            data_frame = pd.DataFrame(links_part, columns=['URL'])  
            file_name = f'links_{i+1}.csv' 
            # path for saving
            data_frame.to_csv(f'{self.output_dir}\\{file_name}', index=False, encoding='utf-8')  

        # Additionally save all links in one file (same as before)
        data_frame = pd.DataFrame(filtered_links, columns=['URL'])  
        data_frame.to_csv(f'{self.output_dir}\\all_links.csv', index=False, encoding='utf-8')  

print("link scraper class is working good")

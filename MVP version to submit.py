import requests
from bs4 import BeautifulSoup
import re
import math
import requests
import pandas as pd 

#_____________________________________________________________________________________________
# extracting links

# generate the group links (for 333 pages or less)
def generate_page_links(base_link, total_pages):
    page_links = [base_link]
    for p in range(2, total_pages + 1):
        page_links.append(base_link + "&page=" + str(p))
    return page_links

# extract all the linkes items for sale 
def extract_links_from_page(session, page_link):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = session.get(page_link, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    links = []
    for tag_a in soup.find_all('a', class_="card__title-link", href=True):
        links.append(tag_a['href'])
    return links

# filter "new real estate project" links
def filter_links(links):
    return [link for link in links if "/new-real-estate-project-" not in link]

# save the links in a csv file
def save_links_to_csv(links, file_path, num_files):
    links_per_file = math.ceil(len(links) / num_files)
    
    for i in range(num_files):
        start_index = i * links_per_file
        end_index = min((i + 1) * links_per_file, len(links))
        links_chunk = links[start_index:end_index]

        df = pd.DataFrame(links_chunk, columns=['URL'])
        file_name = f'{file_path}/links_{i+1}.csv'
        df.to_csv(file_name, index=False, encoding='utf-8')


# calling functions to extract links

base_link = 'https://www.immoweb.be/en/search/house-and-apartment/for-sale?countries=BE&amp%3BorderBy=relevance&amp%3Bpage=2'
total_pages = 333

# calling to generate 333 grope page links
page_links = generate_page_links(base_link, total_pages)

# extract the links of sale items from 333 group pages (extracting +10000 links)
session = requests.Session()
all_links = []
for page_link in page_links[:3]:  # we can choose wor on 333 pages or less
    all_links.extend(extract_links_from_page(session, page_link))

# calling to filter the "new real estate project" links
filtered_links = filter_links(all_links)

# calling to save the extracted links to a csv file
save_links_to_csv(filtered_links, 'C:\\Users\\becod\\AI\\my-projects\\Majid_immoeliza_scraping\\Majid_mustafa\\Immo_scrapping_draft\\Links', 10)

print("the links saved in csv file")

#_____________________________________________________________________________________________
#  Extracting detailes

# request to URL to extract tht HTML content
def get_soup(url):
    headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"}
    req = requests.get(url, headers=headers)
    soup = BeautifulSoup(req.content, "html.parser")
    return soup

# extracting Property ID
def get_property_id(soup):
    try:
        html = soup.find("meta", {'property': "og:url"}).get('content')
        html_list = html.split("/")
        return html_list[-1]
    except Exception as e:
        print(f"Error in Property_ID: {e}")
        return None

# extracting Postal code
def get_postal_code(html_list):
    try:
        return html_list[-2]
    except Exception as e:
        print(f"Error in postal_code : {e}")
        return None

# extracting Locality (city)
def get_locality(html_list):
    try:
        return html_list[-3]
    except Exception as e:
        print(f"Error in locality : {e}")
        return None

# extracting price
def get_price(soup):
    try:
        home_meta_info = soup.find_all("div", {'class': 'grid__item desktop--9'})
        price = home_meta_info[0].find("p", {'class': 'classified__price'}).find_all('span', {'class':'sr-only'})[0].text.strip()
        price = re.sub(r'[^\d.,\-+]', '', price)
        return price
    except Exception as e:
        print(f"Error in price : {e}")
        return None

# Type of property
def get_property_type(html_list):
    try:
        return html_list[-5]
    except Exception as e:
        print(f"Error in Type_of_property: {e}")
        return None

# extracting number of bedrooms
def get_bedrooms(soup):
    try:
        home_prop_info = soup.find_all("div", {'class': 'text-block__body'})[0].find_all("div", {'class': 'overview__column'})
        bed_rooms =home_prop_info[0].find_all("div", {'class': 'overview__item'})[0].find_all('span', {'class':'overview__text'})[0].text.strip()
        bed_rooms = re.search(r'\d+', bed_rooms)
        return bed_rooms.group() if bed_rooms else None
    except Exception as e:
        print(f"Error in bed_rooms : {e}")
        return None

# extracting Living area size
def get_living_area(soup):
    try:
        home_prop_info = soup.find_all("div", {'class': 'text-block__body'})[0].find_all("div", {'class': 'overview__column'})
        space = home_prop_info[1].find_all("div", {'class': 'overview__item'})[0].find_all('span', {'class':'overview__text'})[0].text.strip()
        space = re.findall(r'\d+', space)[0]
        return space
    except Exception as e:
        print(f"Error in space: {e}")
        return None

# extracting kitchen type
def get_kitchen(soup):
    try:
        kitchen_keywords = ('Kitchen type', 'Type of kitchen')
        kitchen_th = soup.find('th', string=lambda x: x and x.strip() in kitchen_keywords)
        if kitchen_th:
            kitchen = kitchen_th.find_next_sibling('td').contents[0].strip()
            return 1 if kitchen in ('Installed','Installed', 'Hyper equipped', 'USA  Hyper equipped','Semi equipped','USA hyper equipped') else 0
        return 0
    except Exception as e:
        print(f"Error in kitchen: {e}")
        return None

# extracting state of building
def get_building_condition(soup):
    try:
        building_condition_header = soup.find('th', string=lambda x: x and x.strip() == 'Building condition').find_parent('tr')
        return building_condition_header.find('td', class_='classified-table__data').contents[0].strip()
    except Exception as e:
        print(f"Error in building_condition: {e}")
        return None

# extracting number of frontages (facades)
def get_number_of_facades(soup):
    try:
        facade_keywords = re.compile(r'Number of (frontages|facades)', re.IGNORECASE)
        facades_th = soup.find('th', string=facade_keywords)
        return facades_th.find_next_sibling('td').contents[0].strip() if facades_th else None
    except Exception as e:
        print(f"Error in Number_of_facades : {e}")
        return None

# extracting furnished or not
def get_furnished(soup):
    try:
        Furnished = soup.find('th', string=lambda x: x and x.strip() == 'Furnished').find_next_sibling('td').contents[0].strip()
        return 1 if Furnished == 'Yes' else 0
    except Exception as e:
        print(f"Error in Furnished: {e}")
        return 0

# extracting fire place state
def get_open_fire(soup):
    try:
        Open_fire = soup.find('th', string=lambda x: x and x.strip() == 'How many fireplaces?').find_next_sibling('td').contents[0].strip()
        return 1 if Open_fire else 0
    except Exception as e:
        print(f"Error in Open_fire: {e}")
        return 0

# extracting swimming pool state
def get_swimming_pool(soup):
    try:
        Swimming_pool = soup.find('th', string=lambda text: text and 'Swimming pool' in text.strip()).find_next_sibling('td').contents[0].strip()
        return 1 if Swimming_pool == 'Yes' else 0
    except Exception as e:
        print(f"Error in Swimming_pool: {e}")
        return 0

# extracting garden state
def get_garden(soup):
    try:
        garden = soup.find('th', string=re.compile(r'^Garden.*')).find_next_sibling('td').contents[0].strip()
        return garden if garden else None
    except Exception as e:
        print(f"Error in garden: {e}")
        return None

# extracting trass state
def get_terrace(soup):
    try:
        Terrace = soup.find('th', string=re.compile(r'^Terrace.*')).find_next_sibling('td').contents[0].strip()
        return Terrace if Terrace else None
    except Exception as e:
        print(f"Error in Terrace: {e}")
        return None

# calling all functions
def request_url(url):
    soup = get_soup(url)
    html_list = soup.find("meta", {'property': "og:url"}).get('content').split("/")
    
    property_details = {
        'Property ID': get_property_id(soup),
        'Postal code': get_postal_code(html_list),
        'Locality name': get_locality(html_list),
        'Price': get_price(soup),
        'Type of property': get_property_type(html_list),
        'Number of rooms': get_bedrooms(soup),
        'Living area': get_living_area(soup),
        'Equipped kitchen': get_kitchen(soup),
        'State of building': get_building_condition(soup),
        'Number of facades': get_number_of_facades(soup),
        'Furnished': get_furnished(soup),
        'Open fire': get_open_fire(soup),
        'Swimming pool': get_swimming_pool(soup),
        'Garden (m²)': get_garden(soup),
        'Terrace (m²)': get_terrace(soup)
    }

    return property_details

#_____________________________________________________________________________________________
#  calling and saving


# reading input file (linkes)
def read_input_file(file_path):
    try:
        df = pd.read_csv(file_path)
        return df['URL'].tolist()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return []

# process the links and extract the details of sale items
def process_urls(url_list):
    property_details = []
    for url in url_list:
        property_details.extend(request_url(url)) 
    return property_details

# saving the details of sale items
def write_output_file(file_path, property_details):
    try:
        df_properties = pd.DataFrame(property_details)
        df_properties.to_csv(file_path, index=False, encoding='utf-8')
        print(f"CSV file created: {file_path}")
    except Exception as e:
        print(f"Error writing to file {file_path}: {e}")

# Main function to process all files
def process_files(num_files, input_file_template, output_file_template):
    for i in range(1, num_files + 1):  # Loop from 1 to num_files
        input_file_path = input_file_template.format(i)
        output_file_path = output_file_template.format(i)
        
        # reading the input file and extract the links
        url_list = read_input_file(input_file_path)
        
        # process the links and extract the detail of items
        property_details = process_urls(url_list)
        
        # save the extracted detail in output file
        write_output_file(output_file_path, property_details)

# setting the paths and number of files
num_files = 10
input_file_path = "C:\\Users\\becod\\AI\\my-projects\\Majid_immoeliza_scraping\\Majid_mustafa\\Immo_scrapping_draft\\Links\\links_{}.csv"
output_file_path_template = "C:\\Users\\becod\\AI\\my-projects\\Majid_immoeliza_scraping\\Majid_mustafa\\Immo_scrapping_draft\\output\\property_details_{}.csv"

# calling the main function 
process_files(num_files, input_file_path, output_file_path_template)

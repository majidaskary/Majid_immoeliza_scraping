import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

List_url = [
    "https://www.immoweb.be/en/classified/penthouse/for-sale/etterbeek/1040/20232667",
    "https://www.immoweb.be/en/classified/house/for-sale/kortrijk/8500/20234460",
    "https://www.immoweb.be/nl/zoekertje/huis/te-koop/amay/4540/20215296",
    "https://www.immoweb.be/en/classified/house/for-sale/wavre/1300/20231046",
    "https://www.immoweb.be/en/classified/apartment/for-sale/saint-gilles/1060/20234144",
]


def request_url(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
    }
    req = requests.get(url, headers=headers)
    soup = BeautifulSoup(req.content, "html.parser")
    property_details = []

    try:
        html = soup.find("meta", {"property": "og:url"}).get("content")
        html_list = html.split("/")
        Property_ID = html_list[-1]
    except:
        Property_ID = None
    try:
        postal_code = html_list[-2]
    except:
        postal_code = None
    try:
        locality = html_list[-3]
    except:
        locality = None
    try:
        home_meta_info = soup.find_all("div", {"class": "grid__item desktop--9"})
        price = (
            home_meta_info[0]
            .find("p", {"class": "classified__price"})
            .find_all("span", {"class": "sr-only"})[0]
            .text.strip()
        )
        print(price)
    except:
        price = None
    try:
        Type_of_property = (
            home_meta_info[0]
            .find("h1", {"class": "classified__title"})
            .text.strip()[0:11]
        )  # the second [0:11] just to return the property type
    except:
        Type_of_property = None
    try:
        home_prop_info = soup.find_all("div", {"class": "text-block__body"})[
            0
        ].find_all("div", {"class": "overview__column"})
        bed_rooms = (
            home_prop_info[0]
            .find_all("div", {"class": "overview__item"})[0]
            .find_all("span", {"class": "overview__text"})[0]
            .text.strip()
        )
    except:
        bed_rooms = None
    try:
        space = (
            home_prop_info[1]
            .find_all("div", {"class": "overview__item"})[0]
            .find_all("span", {"class": "overview__text"})[0]
            .text.strip()
        )
        space = re.findall(r"\d+", space)[0]  # Extract only the digits
    except:
        space = None
    ######################## check this one again for different name ######################## try elif on the original one
    try:
        kitchen_keywords = (
            "Kitchen type",
            "Type of kitchen",
        )  # as sometimes it has one of these names
        kitchen_th = soup.find(
            "th", string=lambda x: x and x.strip() in kitchen_keywords
        )
        if kitchen_th:
            kitchen = kitchen_th.find_next_sibling("td").contents[0].strip()
            print(kitchen)

            # Now, check for the kitchen types you're interested in
            if kitchen in (
                "Installed",
                "Installed",
                "Hyper equipped",
                "USA  Hyper equipped",
                "Semi equipped",
                "USA hyper equipped",
            ):
                kitchen_type = 1
            else:
                kitchen_type = 0
        else:
            kitchen_type = (
                0  # Default value if 'Kitchen type' or 'Type of kitchen' not found
            )
    except:
        kitchen_type = None
    # Building cindition
    try:
        building_condition_header = soup.find(
            "th", string=lambda x: x and x.strip() == "Building condition"
        ).find_parent("tr")

        building_condition = (
            building_condition_header.find("td", class_="classified-table__data")
            .contents[0]
            .strip()
        )
    except:
        building_condition = None
    # Number of facades   Number of facades
    ############################# the same problem as kitchen, it might be named "Number of facades" #############
    try:
        facades = (
            soup.find("th", string=lambda x: x and x.strip() == "Number of frontages")
            .find_next_sibling("td")
            .contents[0]
            .strip()
        )

        if facades:
            Number_of_facades: facades
        else:
            Number_of_facades: 0
    except:
        facades = None
    # Furnished
    ############################# the same problem as kitchen, it might be named "State of the building" #############
    try:
        Furnished = (
            soup.find("th", string=lambda x: x and x.strip() == "Furnished")
            .find_next_sibling("td")
            .contents[0]
            .strip()
        )
        if Furnished == "Yes":
            Furnished = 1
        else:
            Furnished = 0
    except:
        Furnished = None
    # open fire space
    try:
        Open_fire = (
            soup.find("th", string=lambda x: x and x.strip() == "How many fireplaces?")
            .find_next_sibling("td")
            .contents[0]
            .strip()
        )
        if Open_fire:
            Open_fire = 1
        else:
            Open_fire = 0
    except:
        Open_fire = None
    # Swimming_pool
    try:
        Swimming_pool = (
            soup.find("th", string=lambda x: x and x.strip() == "Swimming pool")
            .find_next_sibling("td")
            .contents[0]
            .strip()
        )
        if Swimming_pool == "Yes":
            Swimming_pool = 1
        else:
            Swimming_pool = 0
    except:
        Swimming_pool = None
    # Garden
    ############################### Different name "Garden area" ###########################
    try:
        garden = (
            soup.find("th", string=lambda x: x and x.strip() == "Garden surface")
            .find_next_sibling("td")
            .contents[0]
            .strip()
        )
        if garden:
            garden = garden
        else:
            garden = None
    except:
        garden = None
    # Terrace
    ################################## It might have value only "Yes" or differnt name like "Terrace surface area" #########################
    try:
        Terrace = (
            soup.find("th", string=lambda x: x and x.strip() == "Terrace surface")
            .find_next_sibling("td")
            .contents[0]
            .strip()
        )
        if Terrace:
            Terrace = Terrace
        else:
            Terrace = None

    except:
        Terrace = None

    property_details.append(
        {
            "Property ID": Property_ID,
            "Postal code": postal_code,
            "Locality name": locality,
            "Price": price,
            "Type of property": Type_of_property,
            "Number of rooms": bed_rooms,
            "Living area": space,
            "Equipped kitchen": kitchen_type,
            "State of building": building_condition,
            "Number of facades": facades,
            "Furnished": Furnished,
            "Open fire": Open_fire,
            "Swimming pool": Swimming_pool,
            "Garden (m²)": garden,
            "Terrace (m²)": Terrace,
        }
    )

    return property_details


# Assuming List_url contains your URLs
all_property_details = []
for url in List_url:
    all_property_details.extend(request_url(url))

# Convert the list of dictionaries to a Pandas DataFrame
df = pd.DataFrame(all_property_details)

# Save the DataFrame to a CSV file
df.to_csv(
    "C:\\Users\\mgabi\\Desktop\\becode\\becode_projects\\immoweb_scraping\\property_details.csv",
    index=False,
    encoding="utf-8",
)

print("CSV file created")

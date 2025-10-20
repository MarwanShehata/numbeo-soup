""" This script uses BeautifulSoup to parse through Numbeo pages and extract all cost-of-living data including price ranges. """

import re
import time
import random
from bs4 import BeautifulSoup
import requests

# This section keeps the Numbeo server from being unhappy with us

headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }

# city-list.txt contains a list of cities we want to investigate

city_file = open("city-list.txt", "r")
content = city_file.read()
city_list = content.split("\n")
city_file.close()

# This list will store all extracted data
all_data = []

for city in city_list:

    # Handling data quirks and formatting URL
    if len(city) == 0:
        continue
    
    clean_city = city.replace(" ","-")
    url = "https://www.numbeo.com/cost-of-living/in/" + clean_city

    # Making the request
    req = requests.get(url, headers)
    soup = BeautifulSoup(req.content, 'html.parser')

    # Parse all rows from the data table
    all_rows = soup.body.findAll("tr")

    # Extract data from each row
    for row in all_rows:
        cells = row.findAll("td")
        
        # Skip header rows and rows with fewer than 3 cells
        if len(cells) < 3:
            continue
        
        # Get item name (first cell) and price (second cell)
        item_name = cells[0].text.strip()
        price_cell = cells[1].findAll("span", class_="first_currency")
        
        if price_cell:
            price_value = price_cell[0].text.strip()
            
            # Extract range data from the third cell
            range_cell = cells[2]
            range_texts = range_cell.findAll("span", class_="barTextLeft")
            range_min = ""
            range_max = ""
            
            if len(range_texts) >= 1:
                range_min = range_texts[0].text.strip()
            
            range_texts_right = range_cell.findAll("span", class_="barTextRight")
            if len(range_texts_right) >= 1:
                range_max = range_texts_right[0].text.strip()
            
            print(f"{city.strip()},{item_name},{price_value},{range_min},{range_max}")
            
            all_data.append({
                'city': city.strip(),
                'item': item_name,
                'price': price_value,
                'range_min': range_min,
                'range_max': range_max
            })

    # This is here to keep the Numbeo server happy - it doesn't like too many requests
    time.sleep(random.randint(1,9))

# Write the results to output.csv
with open("output.csv", 'w') as f:
    f.write("City,Item,Price,Range Min,Range Max\n")  # Header
    for entry in all_data:
        f.write('%s,%s,%s,%s,%s\n' % (entry['city'], entry['item'], entry['price'], entry['range_min'], entry['range_max']))

print("Data extraction complete! Results written to output.csv")

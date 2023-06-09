import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# Define the URL of the site
base_url = 'https://data.un.org'
page_url = "/default.aspx"

fetch_all = True  # set this to False if you want to fetch all links
response = requests.get(base_url + page_url)
soup = BeautifulSoup(response.text, "html.parser")

# Find the "CountryList" div and then get the list of country links
country_list = soup.find("div", class_="CountryList")

# Extract href for each country
countries = country_list.find_all('a')
country_links = [base_url + "/" + country.get('href') for country in countries if country.get('href').startswith('en/iso')]

if fetch_all:
    country_links = country_links[:100]  # limit to first 100

# Indicators of interest
indicators = [
    'GDP: Gross domestic product',
    'GDP growth rate',
    'GDP per capita',
    'Economy: Agriculture',
    'Economy: Industry',
    'Economy: Services and other activity',
    'Unemployment',
    'Labour force participation rate',
    'Balance of payments, current account',
    'CPI: Consumer Price Index'
]

# Master dataframe to store data for all countries
master_df = pd.DataFrame()

# Iterate over each country link
for link in country_links:
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find the economic indicators table
    summary = soup.find('summary', string='Economic indicators')
    
    # If summary is None, print page content and continue with the next iteration
    if summary is None:
        print(f"Cannot find 'Economic indicators' in {link}. Page content:\n{soup.prettify()}")
        continue
    
    table = summary.find_next_sibling('table')
    
    # Extract table headers (years)
    header_years = [2010,2015,2021]
    
    # Extract country name
    country_name = soup.find('td', class_='countrytable').text
    country_name = re.sub(r'\W+', ' ', country_name)
    try:
        print(country_name)
    except UnicodeEncodeError:
         print(country_name.encode('utf-8'))
    # Create a dataframe for the country
    data = {'CountryName': country_name, 'Year': header_years}

    # Add columns for each indicator
    for i, indicator in enumerate(indicators):
            data[indicator] = 'NA'
    
    myDataFrame = pd.DataFrame(data)

    print(myDataFrame)
    # Iterate over rows of the table and update the dataframe
    rowData = dict()
    for row in table.find_all('tr')[1:]:
        cells = row.find_all('td')
        # Check if the row starts with any of the indicators
        for ind in indicators:
            if cells[0].text.strip().startswith(ind):
                cell_values = [cell.text if cell.text != '...' else 'NA' for cell in cells[1:]]
                rowData[ind] = cell_values

        # Update the dataframe with the data and concat it to the data frame
        for i in range(len(header_years)):
            for indicator, values in rowData.items():
                myDataFrame.loc[i, indicator] = values[i]

    # Append the individual country dataframe to the master dataframe
    master_df = pd.concat([master_df, myDataFrame], ignore_index=True)

# Save the dataframe to a csv file
master_df.to_csv('spider_soup.csv', index=False)

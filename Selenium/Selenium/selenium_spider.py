
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
from time import sleep


# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode
chrome_options.add_argument("--disable-feature=NotificationPrompts")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--log-level=3")  # Suppress browser console output

master_df = pd.DataFrame()


# Set up the Chrome driver
driver = webdriver.Chrome(options=chrome_options)

# Navigate to the website
driver.get("http://data.un.org/")

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

header_years = [2010,2015,2021]
name = 'country_spider'
start_urls = ['http://data.un.org/']
ScrapMin100 = True  # Set this to False to get all links
max_links = 10 if ScrapMin100 else None
processed_links = 0


# Find country elements using XPath
country_elements = driver.find_elements(By.XPATH, '//div[contains(@class, "CountryList")]//a[starts-with(@href, "en/iso")]')

# Extract country names from the href attribute value
country_names = [element.get_attribute("href").split('/')[-1] for element in country_elements]


list_links = []
for name in country_names:
    list_links.append('http://data.un.org/en/iso/' + name)
    processed_links += 1
    
    if max_links and processed_links >= max_links:
        break


myDataFrame = pd.DataFrame()

# Open each link and fetch country name
for link in list_links:
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(link)
    sleep(2)
    try: 
        # Find the details element containing the table
        details_element = driver.find_element(By.XPATH, '//summary[text()="Economic indicators"]/ancestor::details')

        # Expand the details element to reveal the table
        driver.execute_script("arguments[0].setAttribute('open', '')", details_element)

        # Find the table element
        table_element = details_element.find_element(By.XPATH, './table')

        # Find all rows in the table body
        rows = table_element.find_elements(By.XPATH, './/tbody/tr')
        # Find the parent element of the country name text
        parent_element = driver.find_element(By.XPATH, '//td[@class="countrytable"]')
        
        # Extract the country name from the parent element
        country_name = parent_element.text
        print(country_name) # log the country name to the console
        # Define the output file path
        output_file = 'countries-selenium.csv'

       

            # Create a dataframe for the country
        data = {
                'CountryName': country_name,
                'Year': header_years,
            }

        for i, indicator in enumerate(indicators):
                data[indicator] = 'NA'
                
        myDataFrame= pd.DataFrame(data) 

        
        # Write the data rows
        rowData = dict()
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            indr = cells[0].text
            for ind in indicators:
                if indr.startswith(ind):
                    rowData[ind] = [cell.text if cell.text != '...' else 'NA' for cell in cells[1:]]

 
        # Write the data rows
        for i in range(len(header_years)):
            for indicator, values in rowData.items():
                myDataFrame.loc[i, indicator] = values[i]
        print(myDataFrame)
            # Append the individual country dataframe to the master dataframe
        master_df = pd.concat([master_df, myDataFrame], ignore_index=True)
    except NoSuchElementException:
        print("Element not found. Unable to locate Economic indicators.")

# Output master dataframe as a CSV file
master_df.to_csv('countries-selenium.csv', index=False)
# Print a success message
print(f"Table data has been scraped and saved to '{output_file}'.")
    # Close the webdriver
driver.quit()
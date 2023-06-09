
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
from time import sleep


# Set up Chrome options
# to open the browser in headless mode and prevenet the browser from opening
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode
chrome_options.add_argument("--disable-feature=NotificationPrompts")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--log-level=3")  # Suppress browser console output


# Set up the Chrome driver
driver = webdriver.Chrome(options=chrome_options)

# Navigate to the website
driver.get("http://data.un.org/")

# define the master dataframe and other variables
# Define the output file path
output_file = 'countries-selenium.csv'
master_df = pd.DataFrame()
myDataFrame = pd.DataFrame()
header_years = [2010,2015,2021]
ScrapMin100 = True  # Set this to False to get all links
max_links = 3 if ScrapMin100 else None
processed_links = 0
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


# Find country elements using XPath
country_elements = driver.find_elements(By.XPATH, '//div[contains(@class, "CountryList")]//a[starts-with(@href, "en/iso")]')

# Extract country names from the href attribute value
country_href = [element.get_attribute("href").split('/')[-1] for element in country_elements]

list_links = []
for name in country_href:
    list_links.append('http://data.un.org/en/iso/' + name)
    processed_links += 1
    
    if max_links and processed_links >= max_links:
        break

# Open each link and fetch country name
for link in list_links:
    driver = webdriver.Chrome(options=chrome_options)
    # here we open the link for each country and give it a sleep time of 2 seconds
    driver.get(link)
    sleep(2)
    try: 

        # Find the parent element of the country name text
        parent_element = driver.find_element(By.XPATH, '//td[@class="countrytable"]')
        
        # Extract the country name from the parent element
        country_name = parent_element.text

        # Find the details element containing the table under economic indicators
        details_element = driver.find_element(By.XPATH, '//summary[text()="Economic indicators"]/ancestor::details')

        # Expand the details element to reveal the table
        driver.execute_script("arguments[0].setAttribute('open', '')", details_element)

        # Find the table element
        table_element = details_element.find_element(By.XPATH, './table')

        # Find all rows in the table body
        rows = table_element.find_elements(By.XPATH, './/tbody/tr')
      
        # Print the country name to make sure we are on the right track
        print(country_name) 
        

        # Create a dataframe for the country
        data = {
                'CountryName': country_name,
                'Year': header_years,
            }

        # Add columns for each indicator
        for i, indicator in enumerate(indicators):
                data[indicator] = 'NA'
                
        myDataFrame= pd.DataFrame(data) 
        
        # loop through the rows and extract the data and update the dataframe for each country
        rowData = dict()
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            indr = cells[0].text
            for ind in indicators:
                if indr.startswith(ind):
                    rowData[ind] = [cell.text if cell.text != '...' else 'NA' for cell in cells[1:]]

 
        # Update the dataframe with the data and concat it to the myDataFrame 
        for i in range(len(header_years)):
            for indicator, values in rowData.items():
                myDataFrame.loc[i, indicator] = values[i]

        # again print to make sure we are on the right track        
        print(myDataFrame)
        
        # Append the individual country dataframe to the master dataframe
        # our master dataframe will be converted to csv file at the end
        master_df = pd.concat([master_df, myDataFrame], ignore_index=True)

    # here we are handling exceptions if the element is not found
    except NoSuchElementException:
        print("Element not found. Unable to locate Economic indicators.")

# Output master dataframe as a CSV file
master_df.to_csv('countries-selenium.csv', index=False)
# Print a success message
print(f"Table data has been scraped and saved to '{output_file}'.")
    # Close the webdriver
driver.quit()
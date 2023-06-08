import scrapy
import pandas as pd
import csv

class CountrySpider(scrapy.Spider):
    name = 'country_spider'
    start_urls = ['http://data.un.org/']
    ScrapMin100 = False  # Set this to False to get all links
    max_links = 100 if ScrapMin100 else None
    processed_links = 0
    linksList = []
    headers = []
    data = []
    df = pd.DataFrame()
    
    def __init__(self):
        self.master_df = pd.DataFrame()  # master dataframe

    def parse(self, response):
        xpath = '//div[contains(@class, "CountryList")]//a[starts-with(@href, "en/iso")]/@href'

        selection = response.xpath(xpath).getall()

        selection = response.xpath(xpath)
        for s in selection:
            if self.max_links and self.processed_links >= self.max_links:
                break
            self.processed_links += 1
            self.linksList.append('http://data.un.org/' + s.get())
            yield scrapy.Request(self.linksList[-1], callback=self.parse_country)

    def parse_country(self, response):
        # Extract country name
        country_name = response.xpath('//td[@class="countrytable"]/text()').get()

        # Extract table headers (years)
        header_years = response.xpath('//summary[text()="Economic indicators"]/following-sibling::table//thead/tr/td/text()').getall()
        header_years = [year.strip() for year in header_years]
        self.headers = ['Country Name', 'Year'] + header_years
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
       
         # Create a dataframe for the country
        data = {
            'CountryName': country_name,
            'Year': header_years,
        }

        for i, indicator in enumerate(indicators):
            data[indicator] = 'NA'
            
        # Create a dataframe for the country
        self.df = pd.DataFrame(data)

        # Initialize data lists for each header
        self.data = [[] for _ in self.headers]

       
        rowData = dict()
        rows = response.xpath('//summary[text()="Economic indicators"]/following-sibling::table//tbody/tr')
        for row in rows:
            # Check if the row starts with any of the indicators
            indicator = row.xpath('td[1]/text()').get()
            if any(indicator.startswith(ind) for ind in indicators):
                # Extract the values under each header for the row
                values = row.xpath('td[position()>1]/small/text()').getall()
                values = [value.strip() if value.strip() != '...' else 'NA' for value in values]
                rowData[indicator] = values
            
        
      

        for i in range(len(header_years)):
            for indicator, values in rowData.items():
                self.df.loc[i, indicator] = values[i]
        
       
        # Append the individual country dataframe to the master dataframe
        self.master_df = pd.concat([self.master_df, self.df], ignore_index=True)


    def output_csv(self):
    # Output master dataframe as a CSV file
        self.master_df.to_csv('countries.csv', index=False)
    def close(self, reason):
        self.output_csv()  # This will write the final DataFrame to a csv

        


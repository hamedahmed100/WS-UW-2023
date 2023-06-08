import scrapy
import csv

class Link(scrapy.Item):
    link = scrapy.Field()

class CountrySpider(scrapy.Spider):
    name = 'country_spider'
    start_urls = ['http://data.un.org/']
    ScrapMin100 = True  # Set this to False to get all links
    max_links = 10 if ScrapMin100 else None
    processed_links = 0
    linksList = []
    country_data = []

    def parse(self, response):
        xpath = '//div[contains(@class, "CountryList")]//a[starts-with(@href, "en/iso")]/@href'

        selection = response.xpath(xpath).getall()
        
        selection = response.xpath(xpath)
        for s in selection:
            if self.max_links and self.processed_links >= self.max_links:
                break
            self.processed_links += 1
            l = Link()
            l['link'] = 'http://data.un.org/' + s.get()
            link = l['link']

            self.linksList.append(link)
            yield scrapy.Request(link, callback=self.parse_country)

    def parse_country(self, response):
        # Extract country name
        country_name = response.xpath('//td[@class="countrytable"]/text()').get()

        # Extract table headers
        headers = response.xpath('//details[summary="Economic indicators"]/table/thead/tr/td/text()').getall()
        headers = ['Country Name', 'Year'] + headers[0:]  # Add 'Country Name' and 'Year' to headers list

        # Extract table data
        data_rows = response.xpath('//details[summary="Economic indicators"]/table/tbody/tr')
        for row in data_rows:
            # Extract year from the first column of each row
            year = row.xpath('td[1]/small/text()').get()

            # Extract values for the specified headers
            values = row.xpath('td[position() > 1]/small/text()').getall()

            # Create a dictionary with the extracted data
            country_data = dict(zip(headers, [country_name, year] + values))

            # Append the country data to the spider's country_data list
            self.country_data.append(country_data)

        # Check if all links have been processed
        if self.processed_links == len(self.linksList):
            # Write the country data to a CSV file
            with open('country_data.csv', 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                writer.writerows(self.country_data)

            self.log(f'Country data has been saved to country_data.csv')

import scrapy
from ..items import WebScrapyAutoLoginItem
from scrapy.http import FormRequest

class AutoLoginSpider(scrapy.Spider):
    name = "auto_login"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["https://quotes.toscrape.com/login"]


    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.132 Safari/537.36'
    }
    page_number = 1

    def parse(self, response):

        # Extract CSRF token using XPath
        csrf_token = response.xpath("//input[@name='csrf_token']/@value").get()

        # Define login details
        username = "admin"  # Replace with actual username
        password = "123"  # Replace with actual password

        # Submit a FormRequest with CSRF token, username, and password
        return FormRequest.from_response(
            response,
            formxpath="//form",  # Locate the login form
            formdata={
                "csrf_token": csrf_token,
                "username": username,
                "password": password
            },
            callback=self.after_login
        )

    def after_login(self, response):
        # Check if login was successful by looking for a specific element
        items = WebScrapyAutoLoginItem()

        if response.xpath("//a[text()='Logout']"):
            self.logger.info("Login successful!")
            for quote in response.xpath("//div[@class='quote']"):
                items["title"] = quote.xpath("//span[@class='text']/text()").get()
                items["author"] = quote.xpath("//span/small[@class='author']/text()").get()

                yield items


            next_page = response.xpath("//li[@class='next']/a/@href").get()
            print("next_page:\t", next_page)
            if next_page:
                # Follow the link to the next page
                next_page_url = response.urljoin(next_page)
                print("next_page_url==>", next_page_url)
                #yield scrapy.Request(next_page_url, callback=self.parse)
                yield response.follow(next_page_url, callback=self.after_login)


        else:
            self.logger.error("Login failed.")











import scrapy

class BlogSpider(scrapy.Spider):
    name = 'blogspider'
    start_urls = ['http://www.forroemvinil.com/page/2/']

    def __init__(self):
        self.url_list = []
    
    def parse_page(self, response):
        for post_content in response.css('div.entry-content > p'):
            if "Para baixar esse disco" in unicode(post_content.css('::text').extract_first()):
                 self.url_list.append(post_content.css('a ::attr(href)').extract_first())

    def parse(self, response):
        for post in response.css('li.post'):
            post_page = post.css('div.entry-summary > p > a ::attr(href)').extract_first()
            yield scrapy.Request(response.urljoin(post_page), callback=self.parse_page)

        next_page = response.css('div.floatleft > a ::attr(href)').extract_first()
        if next_page:
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse)
        else:
            url_file = open("url_files.txt", "w")
            for item in self.url_list:
                url_file.write("%s\n" % item)
            url_file.close()
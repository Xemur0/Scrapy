import scrapy
from scrapy.http import HtmlResponse

from jobparser.items import JobparserItem


class SuperjobSpider(scrapy.Spider):
    name = 'superjob'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://russia.superjob.ru/vacancy/search/?keywords=python']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@rel='next']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath(
            "//span[@class='-gENC _1TcZY Bbtm8']//@href").getall()
        for link in links:
            yield response.follow(link, callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        name = response.css("h1::text").get()
        salary = response.xpath(
            "//h1/following-sibling::span//text()").getall()
        url = response.url
        yield JobparserItem(name=name, salary=salary, url=url)

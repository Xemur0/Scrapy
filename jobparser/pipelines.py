# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


class JobparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client.vacancies

    def process_salary(self, salary):
        min_salary = None
        max_salary = None
        currency = None

        if len(salary) == 1:
            min_salary = min_salary
            max_salary = max_salary
            currency = currency

        if len(salary) == 7:
            min_salary = int(salary[1].replace('\xa0', '').replace(' ', ''))
            max_salary = int(salary[3].replace('\xa0', '').replace(' ', ''))
            currency = salary[5]

        if len(salary) == 5:
            if salary[0] == 'от':
                min_salary = int(salary[1].replace('\xa0', '')
                                 .replace(' ', ''))
                currency = salary[4]
            if salary[0] == 'до':
                max_salary = int(salary[1].replace('\xa0', '')
                                 .replace(' ', ''))
                currency = salary[4]

        return min_salary, max_salary, currency

    def process_item(self, item, spider):
        if spider.name == 'hhru':
            item['min_salary'], item['max_salary'], item[
                'currency'] = self.process_salary(item['salary'])


        elif spider.name == 'superjob':
            item['_id'] = item['url'].split('-')[-1].split('.')[0]
            item['min_salary'], item['max_salary'], item[
                'currency'] = self.process_sj_salary(item['salary'])

        del item['salary']

        collection = self.mongobase[spider.name]
        collection.insert_one(item)
        return item

    def process_sj_salary(self, salary):
        salary = [i for i in salary if not i.isspace()]

        data_from = None
        data_to = None
        data_currency = None

        for idx, val in enumerate(salary):
            if val == '—':
                data_from = salary[idx - 1]
                data_to = salary[idx + 1]
                data_currency = salary[idx + 2]
            elif val.strip() == 'от':
                data = salary[idx + 1].split()
                data_currency = data.pop()
                data_from = ' '.join(data)
            elif val.strip() == 'до':
                data = salary[idx + 1].split()
                data_currency = data.pop()
                data_to = ' '.join(data)

        return data_from, data_to, data_currency

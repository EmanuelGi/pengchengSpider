from recursive_crawler.spiders.text_spider import RecursiveSpider
import xlrd
import redis
import sys
sys.path.append('../')
import configs
import config

if __name__ == '__main__':

    cfg = configs.Configs(config)
    # xlsx = xlrd.open_workbook('health_websites_ch.xlsx')
    # table = xlsx.sheet_by_index(0)
    # urls = table.col_values(1, 1)

    r = redis.StrictRedis(host=cfg['REDIS_HOST'], port=cfg['REDIS_PORT'], db=0)

    # for url in urls:
    #     r.lpush(RecursiveSpider.redis_key, url)

    xlsx = xlrd.open_workbook('top100-3A-hospital.xlsx')
    table = xlsx.sheet_by_index(0)
    urls = table.col_values(5, 1)
    for url in urls:
        r.lpush(RecursiveSpider.redis_key, url)

# coding: utf-8
import time
import luigi
from luigi.util import requires
from chapter_links import collect_chapter_links
from collect_links import collect_product_links
from parse_page import parse_products
from loguru import logger
from telegram_notify import send_tg

logger.add(f"logs/ikea_{time.strftime('%Y-%m-%d')}.log", rotation="100 MB", encoding="utf-8")
logger.add(send_tg, level=25)


class CollectChapterLinks(luigi.Task):
    chapter_links_file_name = luigi.Parameter(default='data/chapter_links.csv')
    product_links_tmp_file_name = luigi.Parameter(default='data/product_links_tmp_file.csv')

    def output(self):
        return luigi.LocalTarget(self.product_links_tmp_file_name)

    def run(self):
        collect_chapter_links(self.output().path, self.chapter_links_file_name)
        logger.success(f'{self.__class__.__name__} task was finished')


@requires(CollectChapterLinks)
class CollectProductLinks(luigi.Task):
    product_links_file_name = luigi.Parameter(default='data/product_links.csv')
    product_tmp_file_name = luigi.Parameter(default='data/products_tmp.csv')

    def output(self):
        return luigi.LocalTarget(self.product_tmp_file_name)

    def run(self):
        collect_product_links(self.input().path, self.chapter_links_file_name,
                              self.product_links_file_name, self.output().path)
        logger.success(f'{self.__class__.__name__} task was finished')


@requires(CollectProductLinks)
class ParseProducts(luigi.Task):
    products_file_name = luigi.Parameter(default='data/products.csv')

    def output(self):
        return luigi.LocalTarget(self.products_file_name)

    def run(self):
        parse_products(self.product_links_file_name, self.input().path, self.output().path)
        logger.success(f'{self.__class__.__name__} task was finished')

# lunch script for test without luigid
# python -m luigi --module ikea_pipeline ParseProducts --local-scheduler
# lunch script for work
# nohup python -m luigi --module ikea_pipeline ParseProducts

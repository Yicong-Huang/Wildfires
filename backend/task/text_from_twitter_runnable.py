"""
@author: Tingxuan Gu
"""
import logging

import rootpath

rootpath.append()
from backend.data_preparation.crawler.twitter_crawler import TweetCrawler
from backend.data_preparation.dumper.twitter_dumper import TweetDumper
from backend.data_preparation.extractor.twitter_extractor import TweetExtractor
from backend.task.runnable import Runnable

logger = logging.getLogger('TaskManager')


class TextFromTwitter(Runnable):
    """
    This class is responsible for crawling texts from twitter, extracting them and dumping them into database
    """

    def __init__(self):
        self.crawler = TweetCrawler()
        self.extractor = TweetExtractor()
        self.dumper = TweetDumper()

    def run(self, keywords: list = None, region: str = 'United%20States',
            batch_num: int = 20, fetch_from_db: bool = False):
        if keywords is None:
            keywords = ['wildfire']
        logger.info('start crawling')
        self.crawler.keywords = keywords
        self.crawler.region = region  # set region settings for crawler
        if fetch_from_db:
            self.crawler.id_generator = self.crawler.fetch_status_id_from_db()

        try:
            while True:
                data = self.crawler.crawl(keywords, batch_num, fetch_from_db)
                self.crawler.total_crawled_count += len(data)
                self.dumper.insert(self.extractor.extract(data), region)
        except StopIteration:
            logger.info("Crawler Finished")


if __name__ == '__main__':
    # TODO:
    # add comments to explain usage of fetch_from_db parameter
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
    TextFromTwitter().run(fetch_from_db=False, region='Brazil')

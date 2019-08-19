import logging
import os
import time
from datetime import datetime, timedelta, timezone
from typing import List

import numpy as np
import rootpath

rootpath.append()
from backend.task.runnable import Runnable
from backend.data_preparation.connection import Connection
from backend.data_preparation.crawler.prism_crawler import PRISMCrawler
from backend.data_preparation.extractor.bil_extractor import BILExtractor
from backend.data_preparation.dumper.prism_dumper import PRISMDumper

logger = logging.getLogger('TaskManager')


class DataFromPRISM(Runnable):
    def __init__(self):
        self.crawler = PRISMCrawler()
        self.extractor = BILExtractor()
        self.dumper = PRISMDumper()
        self.buffer: List[bytes] = list()

    def run(self, end_clause: int = 7):
        """
            end_clause: number of days we want to crawl
            default = 7
        """
        current_date = datetime.now(timezone.utc).date()
        end_date = current_date - timedelta(days=end_clause)
        with Connection() as conn:
            cur = conn.cursor()
            cur.execute('select date, ppt, tmax, vpdmax from prism_info_master')
            exist_list = cur.fetchall()

            exist_dict = dict()
            for date, ppt, tmax, vpdmax in exist_list:
                exist_dict[date] = (ppt, tmax, vpdmax)

        date = current_date - timedelta(days=1)
        while date >= end_date:
            # skip if exist
            if date in exist_dict:
                logger.info(f'skip: {date}')
                date = date - timedelta(days=1)
                continue

            logger.info(f'fetch: {date}')
            table_of_day = dict()
            keep = True
            for var_idx, var in enumerate(PRISMCrawler.VARIABLES):

                saved_filepath = self.crawler.crawl(date, var)
                if saved_filepath is None:
                    keep = False
                    break

                table_of_day[var]: np.ndarray = self.extractor.extract(saved_filepath)
                # clean up
                os.remove(saved_filepath)

                if table_of_day[var] is None:
                    keep = False
                    break
            if not keep:
                date = date - timedelta(days=1)
                continue

            self.dumper.insert(date, table_of_day['ppt'], table_of_day['tmax'], table_of_day['vpdmax'])
            # finish crawling a day
            date = date - timedelta(days=1)


if __name__ == '__main__':
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
    while True:
        DataFromPRISM().run(200)
        logger.info('[PRISM][finished a round. Sleeping]')
        time.sleep(3600 * 6)

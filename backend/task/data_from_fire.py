import os
import sys
import time
from datetime import datetime, timedelta, timezone
import datetime
import rootpath

from paths import FIRE_DATA_DIR

rootpath.append()
from backend.task.runnable import Runnable
from backend.data_preparation.crawler.fire_crawler import FireCrawler
from backend.data_preparation.extractor.fire_extractor import FireExtractor
from backend.data_preparation.dumper.fire_dumper import FireDumper




class DataFromFire(Runnable):
    """run once per day/week/, not any time"""
    def __init__(self):
        self.crawler = FireCrawler(["California", "Utah"])
        self.extractor = FireExtractor()
        self.dumper = FireDumper()
        self.explored_year = set()
        self.explored_fire = set()
        self.logfile = ""


    def write_log(self):
        pass
    def run(self):
        """
        Interface for runnable
        """
        # get the value of current year
        current_year = datetime.datetime.now().date().year

        # check if the crawler is first time used or continue work
        if not os.path.isdir(FIRE_DATA_DIR): # or change to path exist?
            os.makedirs(FIRE_DATA_DIR)

        # check all links
        print("Detecting all links...")
        all_fire_tuples = self.crawler.extract_all_fires()
        print("Num of links:", len(all_fire_tuples))
        # check for crawled fires from database
        print("Retrieving historical fires...")
        crawled = set(self.dumper.retrieve_all_fires())
        print("Num of historical links:", len(crawled))
        # get the difference between all links and crawled
        print("Calculating the difference...")
        to_crawl = sorted(list(set(all_fire_tuples).difference(crawled)))
        print("Num of new links:", len(to_crawl))
        recent_records = self.dumper.get_recent_records()
        print("Recent records:", recent_records)
        to_crawl = recent_records + to_crawl

        self.crawler.cleanup()
        # generate the final list of urls to crawl
        # url_to_crawl = sorted(self.crawler.generate_url_from_tuple(to_crawl,current_year))

        # start to crawl
        # for url in url_to_crawl:
        #     self.crawler.crawl(url)
        #     # whether a record belongs to a sequence of fire is important
        #     # set up a bool value of this purpose
        #     year = 0
        #     name = url.split("/")[-1]
        #     if_sequence = False if len([f for f in os.listdir(FIRE_DATA_DIR) if not f.startswith('.')]) == 1 else True
        #     for record in [f for f in os.listdir(FIRE_DATA_DIR) if not f.startswith('.')]:
                # for a single fire, there can be multiple stages, which shows how this fire develops and dies out.
                # each stage should be treated as a separate record
        #         absolute_path_folder = os.path.join(FIRE_DATA_DIR, record)
        #         single_record = self.extractor.extract(absolute_path_folder, record, if_sequence)
        #         if single_record == dict():
        #             continue
        #         year = self.dumper.insert(single_record)
        #     self.dumper.insert_history(year, name)
        #     self.crawler.cleanup()


        # start crawling
        # id by each fire
        fire_id = 0 if self.dumper.get_latest_fire_id() == None else int(self.dumper.get_latest_fire_id()+1)
        for entry in to_crawl:
            print("FIREID:",fire_id)
            year = entry[0]
            state = entry[1]
            urlname = entry[2]
            if urlname == "ActivePerim":
                continue;
            url = self.crawler.generate_url_from_tuple(year, state, urlname, current_year)
            print("Crawler is crawling:", url)
            self.crawler.crawl(url)
            if_sequence = False if len([f for f in os.listdir(FIRE_DATA_DIR) if not f.startswith('.')]) == 1 else True
            for record in [f for f in os.listdir(FIRE_DATA_DIR) if not f.startswith('.')]:
                # for a single fire, there can be multiple stages, which shows how this fire develops and dies out.
                # each stage should be treated as a separate record
                absolute_path_folder = os.path.join(FIRE_DATA_DIR, record)
                single_record = self.extractor.extract(absolute_path_folder, record, if_sequence, fire_id, state)
                if single_record == dict():
                    continue
                self.dumper.insert(single_record)
            self.dumper.check_if_aggregation_exist(fire_id)
            self.dumper.aggregate(fire_id)
            print("Now fire id is:", fire_id)
            self.dumper.insert_history(year,urlname,state,fire_id, current_year)
            fire_id += 1
            self.crawler.cleanup()
        # finished all insertion







        print("Fire information updated.")
        return








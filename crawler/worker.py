from threading import Thread

from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time
from collections import defaultdict
import json

class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        self.freqDict = defaultdict(int)
        self.highestCount = 0
        self.biggestLink = ""
        self.icsSubDomainDict = defaultdict(set)
        self.visitedHashes = set()
        self.visitedFingerprints = set()
        self.visitedURLS = set()
        self.stopWords = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at",
    "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't", "cannot", "could",
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for",
    "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's",
    "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm",
    "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't",
    "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours",
    "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't",
    "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there",
    "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too",
    "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't",
    "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's",
    "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself",
    "yourselves"
    }
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests in scraper.py"
        assert {getsource(scraper).find(req) for req in {"from urllib.request import", "import urllib.request"}} == {-1}, "Do not use urllib.request in scraper.py"
        super().__init__(daemon=True)
        
    def run(self):
        while (True):
            tbd_url = self.frontier.get_tbd_url()
            # print(f'tbd_url: {tbd_url}')
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                print(f"all visited URLS: {self.visitedURLS}")
                break
            
            resp = download(tbd_url, self.config, self.logger)
            # self.logger.info(
            #     f"Downloaded {tbd_url}, status <{resp.status}>, "
            #     f"using cache {self.config.cache_server}.")
            print("-----------------------------------------------")
            print(f'CURRENT URL POPPED FROM TBD_URL: {tbd_url}')
            print("-----------------------------------------------")
            # print(f'TBD_LIST: {self.frontier.to_be_downloaded}')
            # print()
            # print(f"ALL VISITED URLS: {self.visitedURLS}")

            scraped_urls, (myurl, countHighest) = scraper.scraper(tbd_url, resp, self.freqDict, self.stopWords, self.visitedHashes, self.visitedURLS, self.visitedFingerprints)
            if countHighest > self.highestCount:
                self.highestCount = countHighest
                self.biggestLink = myurl
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)
        
        freqDictSorted = sorted(self.freqDict.items(), key=lambda x: x[1], reverse=True)[:60]

        print(freqDictSorted)
        with open('top50words.txt', 'w') as file:
            file.write(json.dumps(freqDictSorted))
        
        numUniquePages = self.frontier.numUnique
        with open('numUniquePages.txt', 'w') as file:
            file.write(json.dumps(numUniquePages))
        
        with open('biggestURL.txt', 'w') as file:
            file.write(self.biggestLink)
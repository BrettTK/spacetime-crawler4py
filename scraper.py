import re
import os
from urllib.parse import urlparse, urlsplit, urldefrag, urljoin 
import urllib.error
import urllib.robotparser as rbp
from bs4 import BeautifulSoup
from collections import defaultdict
import hashlib

#curtis test git push
#ryan testing git push

def scraper(url, resp, wordFrequency, stopWords, visitedHashes, visitedURLS, visitedFingerprints):
    links, (myurl, countHighest) = extract_next_links(url, resp, wordFrequency, stopWords)

    #print(f'links from XNL: {links}')
    validLinks = [link for link in links if is_valid(link, resp, stopWords, visitedHashes, visitedURLS, visitedFingerprints, wordFrequency)]

    print()

    print(f'VALID LINKS: {validLinks}')
    print()

    # print("NEXT LINKS TO CRAWL:")
    # for index, link in enumerate(validLinks):
    #     print(f'{index}: {link}')
    
    print()
    return validLinks, (myurl, countHighest)
    

def extract_next_links(url, resp, freqDict, stopWords):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    #//TODO IF WE HAVE TIME LMAOOOO
    #fingerprints = set() commented these data structures out because didn't use them yet
    #checksums = set()  
    #duplicates = set()

    listToReturn = []
    countHighest = 0
    the_url = ""
    countHighest = 0

    if resp.status in (200,201,202):
        listToReturn, (the_url, countHighest) = tokenize(resp, freqDict, stopWords)
    return listToReturn, (the_url, countHighest)


def is_valid(url, resp, stopWords, visitedHashes, visitedURLS, visitedFingerprints, freqDict):
    # Decide whether to crawl this url or not.
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    
    #check if the URL 
    #a URL is allowed to be crawled if its robot.txt file +
    
    try:
        parsed = urlparse(url)
        # print(f'url: {url}')
        # if (not parsed.netloc):
        #     return False

        #attempting to check the domain of the parsed url WITHOUT the subdomain included
        try:
            test_domain = urlsplit(url).netloc.split(".")[-4:]
        except:
            return False
        domain = ".".join(test_domain[-3:])

        splitPath = url.split("/")
        lastPart = splitPath[-1]
        
            #ryan added this (not sure if its right)
        if url in visitedURLS:
            #print(f"url already visited: {url}")
            return False
        
        hash = get_fingerprint(resp)
        if hash in visitedHashes:
            return False

        if resp.status not in (200,201,202):
            return False

        #return false for URLS that are not of the following domains
        # if domain not in {"ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu"}:
        #     print(f"invalid DOMAIN: {domain}")
        #     return False
        if not re.match(r"^(.*\.ics.uci.edu/.*|.*\.cs.uci.edu/.*|.*\.informatics.uci.edu/.*|.*\.stat.uci.edu/.*)$", url):
            #print(f"invalid DOMAIN: {url}")
            return False
        if 'events' in splitPath and 'wics' in parsed.netloc:
            #print(f"annoying wics event calendar {url}")
            return False
        if 'page' in splitPath:
            return False
        if parsed.scheme not in {"http", "https"}:
            #print(f"invalid SCHEME: {url}")
            return False
        if "wp-" in parsed.path: # Ryan added this because some jpg files are still being validated despite being put in the re.match() below
            #print(f"contains wp- : {url}")
            return False

        if re.match(r"\d\d\d\d-\d\d-\d\d" + r"|\d\d\d\d-\d\d", lastPart): # no useful information on these pagese
            return False

        if "?" in url:
            #print(f"contains a query / query params: {url}") # added by Ryan because ? or & means a query param which can lead to action=login
            return False

        # robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

        # #figure out if robot.txt tells us if webpage is crawlable, change flag to true if it is 
        
        # roboParser = rbp.RobotFileParser()
        # roboParser.set_url(robots_url)
        # roboParser.read() # makes a request to to the url and is the reason we have try/except

        # if roboParser.can_fetch('*', url) == False: # can fetch doesn't raise any exceptions
        #     #print(f"unfetchable from robots.txt: {roboParser.can_fetch('*', url)}")
        #     return False # since can fetch == isCrawlable(), we return an empty list when can_fetch() is false
     

    except TypeError:
        print ("TypeError for ", parsed)
        raise
    except urllib.error.HTTPError as e: #if read() causes an error -> do something if 404 and do something if not 404
        if e.code != 404:
            #print(f"invalid ERROR CODE: {e.code}")
            return False
    
    flag = re.match(
            r".*\.(css|js|bmp|gif|jpe?g|jpg|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|mpg|sav|jpg|jpeg|midi|qt|txt|ppsx|pps|ear|war|img|apk" 
            + r"|bib|java|xml|htm|php|bam|sam|odc" 
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    if (flag):
        #print(f"invalid FILE TYPE: {parsed.path.lower()}")
        print(f"IGNORED A BAD FILE TYPE: {url}")
        return False

    htmlContent = BeautifulSoup(resp.raw_response.content, 'lxml')
    tokens = re.findall(r"[\x30-\x39\x41-\x5A\x61-\x7A]+", htmlContent.get_text())

    words = [word for word in tokens if word not in stopWords]
    #countDict = defaultdict(int)
    for word in words:
        freqDict[word] += 1
    
    visitedURLS.add(url)
    visitedFingerprints.add(hash)
    ###########################################

    # contentHash = hashFunction(countDict)

    # if contentHash in visitedHashes:
    #     print(f"contentHash already in visitedHashes: {visitedHashes}")
    #     return False
    
    # visitedHashes.add(contentHash)

    # return not re.match(
    #         r".*\.(css|js|bmp|gif|jpe?g|jpg|ico"
    #         + r"|png|tiff?|mid|mp2|mp3|mp4"
    #         + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
    #         + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
    #         + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
    #         + r"|epub|dll|cnf|tgz|sha1"
    #         + r"|thmx|mso|arff|rtf|jar|csv"
    #         + r"|mpg|sav|jpg|jpeg|midi|qt|txt|ppsx|pps|ear|war|img|apk" 
    #         + r"|bib|java|xml|htm|php|bam|sam|odc" 
    #         + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())
    return True

"""
takes in response.raw_response.content

- should be ignoring HTML markup 
- should be putting words into a default dict with their frequencies
- should be using a regex pattern to detect links 

QUESTION: what to do with the dictionary of frequencies of each word

return a list of the URLS 
"""
def tokenize(resp, freqDict, stopWords): # takes in a response object which is used to generate a BeautifulSoup() object and then also accessed for resp.url to generate URLs list
    
    #instantiate a defaultdict to hold the frequencies of all the words found
    #frequencies = defaultdict(int)
    
    #instantiate a BeautifulSoup object to allow manipulation and extraction of data from the webpage
    htmlContent = BeautifulSoup(resp.raw_response.content, 'lxml') #lxml is the most efficient and versatile parser and more effective than the standard
    
    URLS = [urllib.parse.urlsplit(url.get('href'))._replace(fragment='').geturl() for url in htmlContent.find_all('a')]

    # line below should be filtering out all links that start with a "#" because they are already part of the webpage while transforming relative -> absolute URLs

    # URLS = {urljoin(resp.url, link.attrs['href']) for link in htmlContent.find_all('a') if 'href' in link.attrs and link.attrs['href'].startswith('/') and urljoin(resp.url, link.attrs['href']).startswith('http')}

    # ===TOKENIZING STARTS HERE===

    # Split text into words while filtering out words that are considered English stop words
    tokens = re.findall(r"[\x30-\x39\x41-\x5A\x61-\x7A]+", htmlContent.get_text())
    words = [word for word in tokens if word not in stopWords]

    # Count word occurrences
    for word in words:
        freqDict[word] += 1
    
    #returns the list of URLS
    return URLS, (resp.url, len(words))

def hashFunction(count_dict):
    ##################################################
    num_bits = 16 #ONLY NUMBER THAT SHOULD BE CHANGED SHOULD BE NUMBERS DIVISIBLE BY 8
    ##################################################

    finalhash = 0
    x = int(num_bits / 8)
    hash_list = [0] * num_bits
    
    for key in count_dict:
        word_hash = (int.from_bytes(hashlib.sha256(key.encode()).digest()[:x], 'little')) # 32-bit int
        
        bits = [(word_hash >> bit) & 1 for bit in range(num_bits - 1, -1, -1)]

        # print(f'key: {key:<10} bits: {bits} num: {word_hash}')
        for index, bit in enumerate(bits):
            hash_list[index] += count_dict[key] if bit == 1 else (-1 * count_dict[key])
    
    for i in range(len(hash_list)):
        hash_list[i] = 1 if hash_list[i] >= 0 else 0
        finalhash = (finalhash << 1) | hash_list[i]

    return finalhash

def get_fingerprint(resp):
    content = resp.raw_response.content
    fingerprint = hashlib.sha256(content).hexdigest()
    return fingerprint

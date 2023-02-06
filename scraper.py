import re
from urllib.parse import urlparse, urlsplit, urldefrag, urljoin 
import urllib.error
import urllib.robotparser as rbp
from bs4 import BeautifulSoup
from collections import defaultdict
import hashlib

#curtis test git push
#ryan testing git push

def scraper(url, resp, wordFrequency, visitedHashes):
    links = extract_next_links(url, resp, wordFrequency, visitedHashes)
    confirmed_links = [link for link in links if is_valid(link, visitedHashes)]
    

def extract_next_links(url, resp, freqDict, visitedHashes):
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
    if resp.status in (200,201,202):
        listToReturn = tokenize(resp, freqDict, visitedHashes)
    return listToReturn


def is_valid(url, visitedHashes):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    
    #check if the URL 
    #a URL is allowed to be crawled if its robot.txt file +
    try:
        if url in visitedHashes:
            return False
        parsed = urlparse(url)
        
        if (not parsed.netloc):
            return False

        #attempting to check the domain of the parsed url WITHOUT the subdomain included
        domain = urlsplit(url).netloc.split(".")[-3:]
        domain = ".".join(domain)
        print(f'domain: {domain}')

        #return false for URLS that are not of the following domains
        if domain not in {"ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu"}:
            return False
        if parsed.scheme not in {"http", "https"}:
            return False
        
        flag = not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())
        if (flag == False):
            return False
    
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        print(f"robots url: {robots_url}")

        #figure out if robot.txt tells us if webpage is crawlable, change flag to true if it is 
        roboParser = rbp.RobotFileParser()
        roboParser.set_url(robots_url)
        roboParser.read() # makes a request to to the url and is the reason we have try/except

        if roboParser.can_fetch('*', url) == False: # can fetch doesn't raise any exceptions
            return False # since can fetch == isCrawlable(), we return an empty list when can_fetch() is false

    except TypeError:
        print ("TypeError for ", parsed)
        raise
    except urllib.error.HTTPError as e: #if read() causes an error -> do something if 404 and do something if not 404
        if e.code != 404:
            return False
    
    return True

"""
takes in response.raw_response.content 

- should be ignoring HTML markup 
- should be putting words into a default dict with their frequencies
- should be using a regex pattern to detect links 

QUESTION: what to do with the dictionary of frequencies of each word

return a list of the URLS 
"""
def tokenize(resp, freqDict, visitedHashes): # takes in a response object which is used to generate a BeautifulSoup() object and then also accessed for resp.url to generate URLs list
    
    stopWords = {
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
    
    #instantiate a defaultdict to hold the frequencies of all the words found
    #frequencies = defaultdict(int)
    
    #instantiate a BeautifulSoup object to allow manipulation and extraction of data from the webpage
    htmlContent = BeautifulSoup(resp.raw_response.content, 'lxml') #lxml is the most efficient and versatile parser and more effective than the standard 
    URLS = [url.get('href') for url in htmlContent.find_all('a')] 

    # line below should be filtering out all links that start with a "#" because they are already part of the webpage while transforming relative -> absolute URLs

    # URLS = {urljoin(resp.url, link.attrs['href']) for link in htmlContent.find_all('a') if 'href' in link.attrs and link.attrs['href'].startswith('/') and urljoin(resp.url, link.attrs['href']).startswith('http')}

    # ===TOKENIZING STARTS HERE===
    
    # Filter punctuation using regex with the exception of ' and - 
    tokens = re.findall(r"[\x30-\x39\x41-\x5A\x61-\x7A]+", htmlContent.get_text())

    # Split text into words while filtering out words that are considered English stop words
    words = [word for word in tokens if word not in stopWords]

    countDict = defaultdict(int)
    # Count word occurrences
    for word in words:
        freqDict[word] += 1
        countDict[word] += 1
    
    hashOfURL = hashFunction(countDict)
    
    visitedHashes.add(hashOfURL)
    #REMEMBER: do something with the frequencies dict to count the overall frequencies from ALL the webpages
    
    #returns both the list of URLS and dictionary of frequencies as a tuple for later access
    #temporary return values (not sure what to return)
    #return URLS, frequencies
    return URLS

def hashFunction(count_dict):
    #should return a hash, I can try and implement this into the code later, i'm getting finalhash = 3646333053, testfinal = -9529110459, 
    #pretty sure testfinal is wrong, donm't know why though THEY SHOULD BOTH BE RETURNING THE SAME THING AGHHHHHH

    # stringtest = "This is an example sentence."
    # stringtest2 = "why are animals so fucking stubborn sometimes?"

    # tokenlist = re.findall(r"[\x30-\x39\x41-\x5A\x61-\x7A]+", stringtest)
    finalhash = 0
    num_bits = 32
    hash_list = [0] * num_bits
    
    for key in count_dict:
        word_hash = (int.from_bytes(hashlib.sha256(key.encode()).digest()[:4], 'little')) # 32-bit int
        
        bits = [(word_hash >> bit) & 1 for bit in range(num_bits - 1, -1, -1)]

        print(f'key: {key:<10} bits: {bits} num: {word_hash}')
        for index, bit in enumerate(bits):
            hash_list[index] += count_dict[key] if bit == 1 else (-1 * count_dict[key])
    

    for b in hash_list:
        finalhash = (finalhash << 1) + b
    print(f'finalhash: {finalhash}')
    return finalhash
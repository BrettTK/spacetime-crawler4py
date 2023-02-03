import re
from urllib.parse import urlparse, urlsplit
from bs4 import BeautifulSoup
from collections import defaultdict


#curtis test git push
#ryan testing git push

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, res, freqDict):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    listToReturn = []
    if res.status in (200,201,202):
        listToReturn = tokenize(res.raw_response.content, freqDict)
    return listToReturn

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    
    #check if the URL 
    #a URL is allowed to be crawled if its robot.txt file 
    try:
        parsed = urlparse(url)
        
        #attempting to check the domain of the parsed url WITHOUT the subdomain included
        domain = urlsplit(url).netloc.split(".")[-3:]
        domain = ".".join(domain)
        
        #return false for URLS that are not of the following domains
        if domain not in set(["ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stats.uci.edu"]):
            return False
        if parsed.scheme not in set(["http", "https"]):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise

"""
takes in response.raw_response.content 

- should be ignoring HTML markup 
- should be putting words into a default dict with their frequencies
- should be using a regex pattern to detect links 

QUESTION: what to do with the dictionary of frequencies of each word

return a list of the URLS 
"""
def tokenize(rrc, freqDict): #rrc stands for response.raw_response.content
    
#UNCERTAIN: should i generate individual dictionaries for every tokenize() call and not have freqDict as a parameter
#OR update the dictionary of frequencies in the worker class
    
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
    htmlContent = BeautifulSoup(rrc, 'lxml') #lxml is the most efficient and versatile parser and more effective than the standard 
    URLS = [url.get('href') for url in htmlContent.find_all('a')]

    #actual tokenizing starts here; 
    
    # Filter punctuation using regex with the exception of ' and - 
    text = re.sub(r'[^\w\'-]+', ' ', htmlContent.get_text())
    
    # Split words joined by "-"
    text = text.replace("-", " ")
    
    # Lowercase all words so we can accurately count all occurences of a word
    text = text.lower()
    
    # Split text into words while filtering out words that are considered English stop words
    words = [word for word in text.split() if word not in stopWords]
    
    # Count word occurrences
    for word in words:
        freqDict[word] += 1
    
    #REMEMBER: do something with the frequencies dict to count the overall frequencies from ALL the webpages
    
    #returns both the list of URLS and dictionary of frequencies as a tuple for later access
    #temporary return values (not sure what to return)
    #return URLS, frequencies
    return URLS
    